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


def create_advert(email, password, title, description):
    url = f"{base_url}/advert"
    headers = {'Authorization': f'{email}:{password}'}
    try:
        response = requests.post(url, json={'title': title, 'description': description}, headers=headers)
        response.raise_for_status()
        print('Создание объявления:', response.status_code, response.json())
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при создании объявления: {e}")
        if hasattr(e, 'response'):
            print(f"Код статуса: {e.response.status_code}")
            print(f"Ответ сервера: {e.response.text}")
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


def update_advert(email, password, advert_id, title=None, description=None):
    data = {}
    if title:
        data['title'] = title
    if description:
        data['description'] = description
    url = f"{base_url}/advert/{advert_id}"
    headers = {'Authorization': f'{email}:{password}'}
    response = requests.patch(url, json=data, headers=headers)
    print('Update Advert:', response.status_code, response.json())
    return response.json()


def delete_advert(email, password, advert_id):
    url = f"{base_url}/advert/{advert_id}"
    headers = {'Authorization': f'{email}:{password}'}
    response = requests.delete(url, headers=headers)
    print('Delete Advert:', response.status_code, response.json())
    return response.json()


def delete_user(user_id):
    url = f"{base_url}/user/{user_id}"
    response = requests.delete(url)
    print('Delete User:', response.status_code, response.json())
    return response.json()


# Тестирование функциональности

# 1. Создание пользователей
user1 = create_user('user1@example.com', 'password1')
user2 = create_user('user2@example.com', 'password2')

# 2. Создание объявления авторизованным пользователем
advert1 = create_advert(user1['email'], 'password1', 'Продам машину', 'Подержанная машина в отличном состоянии')
if advert1:
    get_advert(advert1['id'])
else:
    print("Не удалось создать объявление")

# 3. Попытка создания объявления неавторизованным пользователем
unauthorized_advert = create_advert('fake@example.com', 'wrongpassword', 'Fake Ad', 'This should fail')

# 4. Получение объявления (доступно всем)
get_advert(advert1['id'])

# 5. Обновление объявления владельцем
update_advert(user1['email'], 'password1', advert1['id'], description='Подержанная машина в идеальном состоянии')

# 6. Попытка обновления объявления не владельцем
update_advert(user2['email'], 'password2', advert1['id'], title='Это не должно сработать')

# 7. Удаление объявления владельцем
delete_advert(user1['email'], 'password1', advert1['id'])

# 8. Попытка удаления несуществующего объявления
delete_advert(user1['email'], 'password1', 9999)

# 9. Обновление данных пользователя
update_user(user1['id'], email='newuser1@example.com', new_password='newpassword1')

# 10. Удаление пользователя
delete_user(user2['id'])

print("Тестирование завершено.")
