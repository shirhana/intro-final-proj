import os
import shutil
import signal
import argparse

from flask import (
    Flask,
    make_response,
    render_template,
    render_template_string,
    send_file,
    redirect,
    request,
    send_from_directory,
    url_for,
    abort,
)
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.serving import run_simple

from utils.path import (
    is_valid_subpath,
    is_valid_upload_path,
    get_parent_directory,
    process_files,
)
from utils.output import error, info, warn, success
from action_types import ActionTypes
from main import run

VERSION = "1.0.0"
PLAYGROUND = "playground-folder"


def read_write_directory(directory: str) -> None:
    """Check if a directory exists and is readable and writable.

    Args:
        directory (str): Path to the directory.

    Returns:
        str: The validated directory path.

    Raises:
        FileNotFoundError: If the specified directory does not exist.
        PermissionError: If the directory is not readable or writable.
    """
    if os.path.exists(directory):
        if os.access(directory, os.W_OK and os.R_OK):
            return directory
        else:
            error("The output is not readable and/or writable")
    else:
        error("The specified directory does not exist")


def parse_arguments():
    """Parse command-line arguments for the application.

    Returns:
        argparse.Namespace: Parsed arguments.
    """
    parser = argparse.ArgumentParser(prog="compressFly")
    cwd = os.getcwd()
    parser.add_argument(
        "-d",
        "--directory",
        metavar="DIRECTORY",
        type=read_write_directory,
        default=PLAYGROUND,
        help="Root directory\n[Default=.]",
    )
    parser.add_argument(
        "-p",
        "--port",
        type=int,
        default=9090,
        help="Port to serve [Default=9090]",
    )
    parser.add_argument(
        "--password",
        type=str,
        default="",
        help="Use a password to access the page. (No username)",
    )
    parser.add_argument(
        "--ssl", action="store_true", help="Use an encrypted connection"
    )

    args = parser.parse_args()

    # Normalize the path
    args.directory = os.path.abspath(args.directory)

    return args


def main() -> None:
    """Main function to run the application."""
    try:
        os.makedirs(PLAYGROUND)
    except FileExistsError:
        pass
    args = parse_arguments()

    app = Flask(__name__)
    auth = HTTPBasicAuth()

    global base_directory
    base_directory = args.directory

    # Deal with Favicon requests
    @app.route("/favicon.ico")
    def favicon():
        """Serve the favicon icon.

        This function serves the favicon icon for the application.
        It retrieves the favicon.ico file
        from the 'static/images' directory and sends it as a
        response with the appropriate mimetype for an icon.

        Returns:
            Response: The HTTP response containing the favicon icon.

        Raises:
            FileNotFoundError: If the favicon.ico file is not found.
            HTTPError: If there are issues with the HTTP request or response.
        """
        return send_from_directory(
            os.path.join(app.root_path, "static"),
            "images/favicon.ico",
            mimetype="image/vnd.microsoft.icon",
        )

    ############################################
    # File Browsing and Download Functionality #
    ############################################
    @app.route("/", defaults={"path": None})
    @app.route("/<path:path>")
    @auth.login_required
    def home(path: str):
        """Handle the home route for file browsing.

        This function serves as the handler for the home route of the
        application, which is responsible
        for file browsing functionality. It checks if the provided path
        is valid, determines whether
        it's a directory or file, and processes the appropriate response
        (either rendering the contents of a directory or downloading a file).

        Args:
            path (str): The path parameter provided in the URL.

        Returns:
            Response: The HTTP response containing the rendered template or
            the file download.

        Raises:
            FileNotFoundError: If the specified path does not exist.
            PermissionError: If there are permission issues with accessing
            the files or directories.
            HTTPError: If there are issues with the HTTP request or response.
        """
        # If there is a path parameter and it is valid
        if path and is_valid_subpath(path, base_directory):
            # Take off the trailing '/'
            path = os.path.normpath(path)
            requested_path = os.path.join(base_directory, path)

            # If directory
            if os.path.isdir(requested_path):
                back = get_parent_directory(requested_path, base_directory)
                is_subdirectory = True

            # If file
            elif os.path.isfile(requested_path):

                # Check if the view flag is set
                if request.args.get("view") is None:
                    send_as_attachment = True
                else:
                    send_as_attachment = False

                # Check if file extension
                (filename, extension) = os.path.splitext(requested_path)
                if extension == "":
                    mimetype = "text/plain"
                else:
                    mimetype = None

                try:
                    return send_file(
                        requested_path,
                        mimetype=mimetype,
                        as_attachment=send_as_attachment,
                    )
                except PermissionError:
                    abort(403, "Read Permission Denied: " + requested_path)

        else:
            # Root home configuration
            is_subdirectory = False
            requested_path = base_directory
            back = ""

        if os.path.exists(requested_path):
            # Read the files
            try:
                directory_files = process_files(
                    os.scandir(requested_path), base_directory
                )
            except PermissionError:
                abort(403, "Read Permission Denied: " + requested_path)

            return render_template(
                "home.html",
                files=directory_files,
                back=back,
                directory=requested_path,
                is_subdirectory=is_subdirectory,
                version=VERSION,
            )
        else:
            return redirect("/")

    #############################
    # File Upload Functionality #
    #############################
    @app.route("/upload", methods=["POST"])
    @auth.login_required
    def upload():
        """Handle file upload functionality.

        This function is triggered when a POST request is made to
        the '/upload' endpoint. It checks
        for the presence of uploaded files, validates the upload path,
        and processes the uploaded
        files based on the specified action type
        (compression or decompression).

        Returns:
            redirect: Redirects the user back to the referrer URL
            after processing the upload.

        Raises:
            FileNotFoundError: If the specified output directory
            does not exist.
            PermissionError: If there are permission issues with reading,
            writing, or deleting files.
            HTTPError: If there are issues with the HTTP request or response.
        """
        if request.method == "POST":

            # No file part - needs to check before accessing the files['file']
            if "file" not in request.files:
                return redirect(request.referrer)

            path = request.form["path"]
            # Prevent file upload to paths outside of base directory
            if not is_valid_upload_path(path, base_directory):
                return redirect(request.referrer)

            action_type = request.form["action"]
            compression_type = request.form["compression_type"]
            error_msg_dict = {}
            for file in request.files.getlist("file"):
                # No filename attached
                if file.filename == "":
                    return redirect(request.referrer)

                if action_type == ActionTypes.COMPRESS.value:
                    filename, extension = os.path.splitext(file.filename)
                    file.save(os.path.join(path, file.filename))
                    output_path = f"{filename}-{compression_type}.bin"
                    try:
                        run(
                            input_paths=[os.path.join(path, file.filename)],
                            output_path=output_path,
                            action_type=action_type,
                            compression_type=compression_type,
                        )
                        os.remove(os.path.join(path, file.filename))
                    except Exception as e:
                        abort(403, e)

                elif action_type == ActionTypes.DECOMPRESS.value:
                    filename, extension = os.path.splitext(file.filename)
                    output_path = file.filename
                    try:
                        file.save(os.path.join(path, output_path))
                        error_msg_dict = run(
                            input_paths=[os.path.join(path, output_path)],
                            output_path=PLAYGROUND,
                            action_type=action_type,
                        )
                        os.remove(os.path.join(path, output_path))
                    except Exception:
                        pass

                # Assuming all is good, process and save out the file
                # TODO:
                # - Add support for overwriting
                if file:
                    if not error_msg_dict == {} and isinstance(
                        error_msg_dict, dict
                    ):
                        error_msg = ""
                        for (
                            ivalid_input_path,
                            error_type,
                        ) in error_msg_dict.items():
                            error_msg += f"* {ivalid_input_path} is "
                            error_msg += f"NOT VALID COMPRESS FILE!\n"
                            error_msg += f"{error_type}\n"
                        abort(403, error_msg)

                    filename = secure_filename(output_path)
                    full_path = os.path.join(path, output_path)
                    try:

                        if action_type == ActionTypes.COMPRESS.value:
                            file.save(full_path)
                            shutil.move(output_path, full_path)

                    except PermissionError:
                        abort(403, "Write Permission Denied: " + full_path)

            return redirect(request.referrer)

    # Password functionality is without username
    users = {"": generate_password_hash(args.password)}

    @auth.verify_password
    def verify_password(username: str, password: str) -> bool:
        """Verify the password for HTTP basic authentication.

        This function is used with Flask-HTTPAuth to verify the password
        for HTTP basic authentication.
        It checks if the provided username exists in the users dictionary
        and then verifies the password using the stored hash.

        Args:
            username (str): The username provided in the HTTP request.
            password (str): The password provided in the HTTP request.

        Returns:
            bool: True if the password is verified successfully,
            False otherwise.

        """
        if args.password:
            if username in users:
                return check_password_hash(users.get(username), password)
            return False
        else:
            return True

    # Inform user before server goes up
    success("Serving {}...".format(args.directory, args.port))

    def handler(signal, frame):
        """Signal handler for handling interrupts.

        This function serves as the signal handler for handling interrupts,
        such as SIGINT (Ctrl+C).
        It prints a message and raises an error indicating that the program
        is exiting.

        Args:
            signal: The signal that triggered the handler (e.g., SIGINT).
            frame: The current stack frame when the signal was received.

        Raises:
            Error: Indicates that the program is exiting due
            to a signal interruption.
        """
        print()
        error("Exiting!")

    signal.signal(signal.SIGINT, handler)

    ssl_context = None
    if args.ssl:
        ssl_context = "adhoc"

    run_simple("0.0.0.0", int(args.port), app, ssl_context=ssl_context)


if __name__ == "__main__":
    """Entry point for the application execution.

    This block of code serves as the entry point for executing the
    application. It first attempts
    to clean the playground folder by removing its contents.
    If the folder doesn't exist, it ignores the FileNotFoundError.
    Then, it calls the main() function to start the application.
    """
    try:
        shutil.rmtree(PLAYGROUND)
    except FileNotFoundError:
        pass

    main()
