with open('free-nature-images.jpg', 'rb') as f:
    data = f.read()
    print(data)
    print(type(data))

    data = data.decode('utf-8')

