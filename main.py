import json
from datetime import datetime
from abc import ABC, abstractmethod

import requests


class Field:

    def __init__(self, value):
        self._value = None
        self.value = value

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value

    def __str__(self) -> str:
        return self.value

    def __eq__(self, input) -> bool:
        if type(input) == self.__class__:
            return self.value == input.value


class Name(Field):
    def __init__(self, value):
        super().__init__(value)

    @staticmethod
    def valid_name(name: str) -> None:
        if type(name) != str:
            raise ValueError("Name must be a string")

    @Field.value.setter
    def value(self, value: str) -> None:
        self.valid_name(value)
        self._value = value


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)

    @staticmethod
    def valid_phone(phone: str) -> None:
        if type(phone) != str:
            raise ValueError("Phone must be a string of numbers")
        if not phone.isdigit():
            raise ValueError("Phone must be a string of numbers")

    @Field.value.setter
    def value(self, value):
        self.valid_phone(value)
        self._value = value


class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)

    @staticmethod
    def valid_birthday(b_day):
        try:
            return str(datetime.strptime(str(b_day), '%Y-%m-%d').date())
        except Exception:
            raise ValueError('Input date format YYYY-MM-DD')

    @Field.value.setter
    def value(self, new_value):
        self._value = self.valid_birthday(new_value)


class Contact:
    def __init__(self, name, phone=None, birthday=None):
        self.name = name
        self.phone = phone
        self.birthday = birthday

    def __str__(self):
        return f'name: {self.name}, phone: {self.phone}, birthday: {self.birthday}'


class ContactList:
    def __init__(self):
        self.contacts = []

    def add_contact(self, contact):
        if contact.value not in [ph.value for ph in self.contacts]:
            self.contacts.append(contact)

    def delete_contact(self, contact):
        if contact.value in [ph.value for ph in self.contacts]:
            self.contacts.remove(contact)

    def find_contact(self, search_term):
        return [str(contact) for contact in self.contacts if search_term in str(contact)]

    def get_contacts(self):
        return [str(contact) for contact in self.contacts]


class DataStorage(ABC):
    @abstractmethod
    def save(self, data):
        pass

    @abstractmethod
    def load(self):
        pass


class JSONDataStorage(DataStorage):
    def __init__(self, filename):
        self.filename = filename

    def save(self, data):
        with open(self.filename, 'w') as file:
            json.dump(data, file, indent=4)

    def load(self):
        with open(self.filename, 'r') as file:
            return_data = json.load(file)
            return return_data


class UserInterface(ABC):
    @abstractmethod
    def run(self):
        pass


class ConsoleUI(UserInterface):
    def __init__(self, data_storage):
        self.data_storage = data_storage
        self.contact_list = ContactList()

    def run(self):
        while True:
            # Отримати введену команду користувача
            user_input = input("Введіть команду (add, delete, find, show, save, load, close): ").strip()

            if user_input == "add":
                # Запитати користувача про дані для нового контакту і створити об'єкт Contact
                name = input("Введіть ім'я контакту: ")
                phone = input("Введіть номер телефону: ")
                birthday = input("Введіть дату народження (YYYY-MM-DD): ")

                contact = Contact(Name(name.capitalize()), Phone(phone), Birthday(birthday))

                # Додати контакт до ContactList
                self.contact_list.add_contact(contact)
                print("Контакт додано!")

            elif user_input == "delete":
                # Запитати користувача про ім'я контакту, який треба видалити
                name_to_delete = input("Введіть ім'я контакту, який треба видалити: ")

                # Видалити контакт із ContactList
                for contact in self.contact_list.contacts:
                    if contact.name == name_to_delete:
                        self.contact_list.delete_contact(contact)
                        print("Контакт видалено!")
                        break
                else:
                    print("Контакт не знайдено.")

            elif user_input == "find":
                # Запитати користувача про пошуковий термін
                search_term = input("Введіть пошуковий термін: ")

                # Знайти контакти, які відповідають пошуковому терміну
                search_results = self.contact_list.find_contact(search_term)
                if search_results:
                    print("Результати пошуку:")
                    for result in search_results:
                        print(result)
                else:
                    print("Збіги не знайдено.")

            elif user_input == "show":
                # Вивести всі контакти
                contacts = self.contact_list.get_contacts()
                if contacts:
                    print("Список контактів:")
                    for contact in contacts:
                        print(contact)
                else:
                    print("Немає збережених контактів.")

            elif user_input == "close":
                print('Програма завершила роботу!')
                break

            elif user_input == "save":
                print('Зберігаємо дані у файл!')
                contacts = self.contact_list.get_contacts()
                self.data_storage.save(contacts)

            elif user_input == "load":
                load_data = self.data_storage.load()
                if load_data:
                    print("Список контактів з файлу:")
                    for contact in load_data:
                        print(contact)
            else:
                print("Невідома команда. Спробуйте ще раз.")


if __name__ == "__main__":
    data_storage = JSONDataStorage('contacts.json')
    console_ui = ConsoleUI(data_storage)
    console_ui.run()
