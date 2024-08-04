import requests

base_url = 'http://127.0.0.1:5000'


def create_user(email, password):
    url = f"{base_url}/user"
    response = requests.post(url, json={'email': email, 'password': password})
    if response.status_code == 201:
        print('Create User:', response.status_code, response.json())
        return response.json()
    elif response.status_code == 409:
        print(f"User already exists, attempting to retrieve by email: {email}")
        return get_user_by_email(email)
    else:
        print(f"Failed to create user: {response.status_code} {response.json()}")
        return None


def get_user_by_email(email):
    url = f"{base_url}/user/email/{email}"
    response = requests.get(url)
    if response.status_code == 200:
        print('Get User by Email:', response.status_code, response.json())
        return response.json()
    else:
        print(f"Failed to get user by email: {response.status_code} {response.json()}")
        return None


def create_advert(user_id, title, description):
    url = f"{base_url}/advert"
    response = requests.post(url, json={'title': title, 'description': description, 'user_id': user_id})
    if response.status_code == 201:
        print('Create Advert:', response.status_code, response.json())
        return response.json()
    else:
        print(f"Failed to create advert: {response.status_code} {response.json()}")
        return None


def get_advert(advert_id):
    url = f"{base_url}/advert/{advert_id}"
    response = requests.get(url)
    print('Get Advert:', response.status_code, response.json())
    return response.json()


def update_user(user_id, email=None, new_password=None):
    data = {}
    if email:
        data['email'] = email
    if new_password:
        data['password'] = new_password
    url = f"{base_url}/user/{user_id}"
    response = requests.patch(url, json=data)
    print('Update User:', response.status_code)
    print('Response content:', response.text)
    print('Update User:', response.status_code, response.json())
    return response.json()


def update_advert(advert_id, title=None, description=None):
    data = {}
    if title:
        data['title'] = title
    if description:
        data['description'] = description
    url = f"{base_url}/advert/{advert_id}"
    response = requests.patch(url, json=data)
    print('Update Advert:', response.status_code, response.json())
    return response.json()


def delete_user(user_id):
    url = f"{base_url}/user/{user_id}"
    response = requests.delete(url)
    print('Delete User:', response.status_code, response.json())
    return response.json()


user = create_user('testuser@example.com', 'securepassword')

advert = create_advert(user['id'], 'For Sale', 'Used car for sale')

get_advert(advert['id'])

update_user(user['id'], email='newemail@example.com', new_password='newsecurepassword')

update_advert(advert['id'], title='For Sale', description='Almost new car for sale')

delete_user(user['id'])
