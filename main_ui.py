import os
import shutil
import signal
import argparse

from flask import Flask, make_response, render_template, render_template_string, send_file, redirect, request, send_from_directory, url_for, abort
from flask_httpauth import HTTPBasicAuth
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.serving import run_simple

from utils.path import is_valid_subpath, is_valid_upload_path, get_parent_directory, process_files
from utils.output import error, info, warn, success
from action_types import ActionTypes
from main import run

VERSION = "0.0.0"
PLAYGROUND = "playground-folder"

def read_write_directory(directory):
    if os.path.exists(directory):
        if os.access(directory, os.W_OK and os.R_OK):
            return directory
        else:
            error('The output is not readable and/or writable')
    else:
        error('The specified directory does not exist')


def parse_arguments():
    parser = argparse.ArgumentParser(prog='compressFly')
    cwd = os.getcwd()
    parser.add_argument('-d', '--directory', metavar='DIRECTORY', type=read_write_directory, default=PLAYGROUND,
                        help='Root directory\n'
                             '[Default=.]')
    parser.add_argument('-p', '--port', type=int, default=9090,
                        help='Port to serve [Default=9090]')
    parser.add_argument('--password', type=str, default='', help='Use a password to access the page. (No username)')
    parser.add_argument('--ssl', action='store_true', help='Use an encrypted connection')
    parser.add_argument('--version', action='version', version='%(prog)s v'+VERSION)

    args = parser.parse_args()

    # Normalize the path
    args.directory = os.path.abspath(args.directory)

    return args


def main():
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
    @app.route('/favicon.ico')
    def favicon():
        return send_from_directory(os.path.join(app.root_path, 'static'),
                                   'images/favicon.ico', mimetype='image/vnd.microsoft.icon')

    ############################################
    # File Browsing and Download Functionality #
    ############################################
    @app.route('/', defaults={'path': None})
    @app.route('/<path:path>')
    @auth.login_required
    def home(path):
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
                if request.args.get('view') is None:
                    send_as_attachment = True
                else:
                    send_as_attachment = False

                # Check if file extension
                (filename, extension) = os.path.splitext(requested_path)
                if extension == '':
                    mimetype = 'text/plain'
                else:
                    mimetype = None

                try:
                    return send_file(requested_path, mimetype=mimetype, as_attachment=send_as_attachment)
                except PermissionError:
                    abort(403, 'Read Permission Denied: ' + requested_path)

        else:
            # Root home configuration
            is_subdirectory = False
            requested_path = base_directory
            back = ''

        if os.path.exists(requested_path):
            # Read the files
            try:
                directory_files = process_files(os.scandir(requested_path), base_directory)
            except PermissionError:
                abort(403, 'Read Permission Denied: ' + requested_path)

            return render_template('home.html', files=directory_files, back=back,
                                   directory=requested_path, is_subdirectory=is_subdirectory, version=VERSION)
        else:
            return redirect('/')

    #############################
    # File Upload Functionality #
    #############################
    @app.route('/upload', methods=['POST'])
    @auth.login_required
    def upload():
        if request.method == 'POST':

            # No file part - needs to check before accessing the files['file']
            if 'file' not in request.files:
                return redirect(request.referrer)

            path = request.form['path']
            # Prevent file upload to paths outside of base directory
            if not is_valid_upload_path(path, base_directory):
                return redirect(request.referrer)
            
            action_type = request.form['action']
            compression_type = request.form['compression_type']
            error_msg_dict = {}
            for file in request.files.getlist('file'):
                # No filename attached
                if file.filename == '':
                    return redirect(request.referrer)

                if action_type == ActionTypes.COMPRESS.value:
                    filename, extension = os.path.splitext(file.filename)
                    output_path = f"{filename}-{compression_type}.bin"
                    run(input_paths=[file.filename], output_path=output_path, action_type=action_type, compression_type=compression_type)

                elif action_type == ActionTypes.DECOMPRESS.value:
                    filename, extension = os.path.splitext(file.filename)
                    output_path = file.filename
                    try:
                        file.save(os.path.join(path,output_path))
                        error_msg_dict = run(input_paths=[os.path.join(path,output_path)], output_path=PLAYGROUND, action_type=action_type)
                        os.remove(os.path.join(path,output_path))
                    except Exception:
                        pass
                    
                # Assuming all is good, process and save out the file
                # TODO:
                # - Add support for overwriting
                if file:
                    if not error_msg_dict == {} and isinstance(error_msg_dict, dict):
                        error_msg = ''
                        for ivalid_input_path, error_type in error_msg_dict.items():
                            error_msg += f'* {ivalid_input_path} is NOT VALID COMPRESS FILE!\n{error_type}\n'
                        abort(403, error_msg)

                    filename = secure_filename(output_path)
                    full_path = os.path.join(path, output_path)
                    try:
                        
                        if action_type == ActionTypes.COMPRESS.value:
                            file.save(full_path)
                            shutil.move(output_path, full_path)
                        

                    except PermissionError:
                        abort(403, 'Write Permission Denied: ' + full_path)

            return redirect(request.referrer)

    # Password functionality is without username
    users = {
        '': generate_password_hash(args.password)
    }

    @auth.verify_password
    def verify_password(username, password):
        if args.password:
            if username in users:
                return check_password_hash(users.get(username), password)
            return False
        else:
            return True

    # Inform user before server goes up
    success('Serving {}...'.format(args.directory, args.port))

    def handler(signal, frame):
        print()
        error('Exiting!')
    signal.signal(signal.SIGINT, handler)

    ssl_context = None
    if args.ssl:
        ssl_context = 'adhoc'

    run_simple("0.0.0.0", int(args.port), app, ssl_context=ssl_context)


if __name__ == '__main__':
    # clean playground folder.. ;)
    try:
        shutil.rmtree(PLAYGROUND)
    except FileNotFoundError:
        pass

    main()