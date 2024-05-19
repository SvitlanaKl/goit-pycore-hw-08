import pickle
from collections import UserDict
from datetime import datetime, timedelta


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    pass

class Phone(Field):
    def __init__(self, value):
        # валідація номеру  перевірка на 10 цифр
        if not value.isdigit() or len(value) != 10:
            raise ValueError("Phone number must contain 10 digits.") 
        # Виклик ініціалізації базового класу
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            # Додайте перевірку коректності даних
            # та перетворіть рядок на об'єкт datetime
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        super().__init__(self.value)
    def __str__(self):
        birthday = self.value.strftime("%d.%m.%Y")
        return birthday

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None
    
    def add_phone(self, phone):
        self.phones.append(Phone(phone))
    
    def remove_phone(self, phone):
        phone_to_remove = next((number for number in self.phones if number.value == phone), None)
        if phone_to_remove:
            self.phones.remove(phone_to_remove)

    def find_phone(self, phone):
        return next((number for number in self.phones if number.value == phone), None)

    def edit_phone(self, old_phone, new_phone):
        phone_to_edit = self.find_phone(old_phone)
        if phone_to_edit:
            self.phones.remove(phone_to_edit)
            self.add_phone(new_phone)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def show_birthday(self):
        pass
    
   
    def __str__(self):
        phones = '; '.join(number.value for number in self.phones)
        birthday = self.birthday if self.birthday else "No birthday set"
        return f"Contact name: {self.name.value}, phones: {phones}, birthday: {birthday}"

class AddressBook(UserDict):

    def add_record(self, record):
        self.data[record.name.value] = record
    
    def find(self, name):
        return self.data.get(name, None)
    
    def delete(self, name):
        removed_record = self.data.pop(name, None)
        if removed_record is None:
            print(f"Record with name '{name}' not found.")
        else:
            print(f"Record with name '{name}' has been deleted.")

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        upcoming_birthdays = []

        for record in self.data.values():
            if record.birthday:
                birthdate = record.birthday.value.date()
                birthdate = birthdate.replace(year=today.year)
                # якщо в цьому році вже минув день народження, змінити в даті рік на наступний
                if birthdate < today:  
                    birthdate = birthdate.replace(year=today.year + 1)
                    
                days_to_birthday = (birthdate - today).days
                
                # якщо день народження потрапляє на вихідні, перенести привітання на наступний тиждень
                if days_to_birthday <= 7:
                    if birthdate.weekday() == 5:
                        birthdate += timedelta(days=2)
                    elif birthdate.weekday() == 6:
                        birthdate += timedelta(days=1)
                    upcoming_birthdays.append({"name": record.name.value, "congratulation_date": birthdate.strftime("%d.%m.%Y")})

        return upcoming_birthdays
    
# серіалізація
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

# десеріалізація
def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "Name doesn't exist."
        except IndexError:
            return "Please give me name"
    return inner

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args

@input_error
def add_contact(args, contacts: AddressBook):
    name, phone = args
    record = Record(name)
    record.add_phone(phone)
    contacts.add_record(record)
    return "Contact added."

@input_error
def change_contact(args, contacts: AddressBook):
    name, old_phone, new_phone = args
    record: Record = contacts.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return "Contact updated."

@input_error
def show_phone(args, contacts: AddressBook):
    name = args[0]
    record: Record = contacts.find(name)
    if record:
        return record
    else:
        return 'Contact not found.'

def show_all(contacts: AddressBook):
    if not contacts:
        return 'No contacts'
    result = ''
    for record in contacts.values():
        result += f'{record}\n'
    return result 
 
@input_error
def add_birthday(args, contacts: AddressBook):
    name, birthday = args
    record: Record = contacts.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added to contact {name}"
    else:
        return f"Contact {name} not found."

@input_error
def show_birthday(args, contacts: AddressBook):
    name = args[0]
    record: Record = contacts.find(name)
    if record:
        return record.birthday
    else:
        return 'Contact not found.'

@input_error  
def birthdays(contacts: AddressBook):
    return contacts.get_upcoming_birthdays()
    

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            save_data(book)
            print("Good bye!")
            break

        elif command == "hello":
            print("How can I help you?")

        elif command == "add":
            print(add_contact(args, book))

        elif command == "change":
            print(change_contact(args, book))

        elif command == "phone":
            print(show_phone(args, book))

        elif command == "all":
            print(show_all(book))

        elif command == "add-birthday":
            print(add_birthday(args, book))
            
        elif command == "show-birthday":
            print(show_birthday(args, book))
            
        elif command == "birthdays":
            print(birthdays(book))
        
        else:
            print("Invalid command.")
    save_data(book)

if __name__ == '__main__':
    main()
