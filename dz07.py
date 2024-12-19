import pickle
import re
from collections import UserDict

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        if not re.fullmatch(r'\d{10}', value):
            raise ValueError("Phone number must be 10 digits.")
        super().__init__(value)

class Birthday(Field):
    def __init__(self, value):
        try:
            self.value = datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name: str):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_phone(self, phone_number: str):
        phone = Phone(phone_number)
        self.phones.append(phone)

    def remove_phone(self, phone_number: str):
        for phone in self.phones:
            if phone.value == phone_number:
                self.phones.remove(phone)
                return
        raise ValueError("Phone number not found.")

    def edit_phone(self, old_phone_number: str, new_phone_number: str):
        for i, phone in enumerate(self.phones):
            if phone.value == old_phone_number:
                self.phones[i] = Phone(new_phone_number)
                return
        raise ValueError("Old phone number not found.")

    def add_birthday(self, birthday: str):
        self.birthday = Birthday(birthday)

    def days_to_birthday(self):
        if not self.birthday:
            return None
        today = datetime.now()
        next_birthday = self.birthday.value.replace(year=today.year)
        if next_birthday < today:
            next_birthday = next_birthday.replace(year=today.year + 1)
        return (next_birthday - today).days

    def find_phone(self, phone_number: str):
        for phone in self.phones:
            if phone.value == phone_number:
                return phone
        return None

    def __str__(self):
        phones_str = "; ".join(p.value for p in self.phones)
        return f"Contact name: {self.name.value}, phones: {phones_str}, birthday: {self.birthday.value.strftime('%d.%m.%Y') if self.birthday else 'N/A'}"

class AddressBook(UserDict):
    def add_record(self, record: Record):
        self.data[record.name.value] = record

    def find(self, name: str):
        return self.data.get(name, None)

    def delete(self, name: str):
        if name in self.data:
            del self.data[name]
        else:
            raise KeyError("Contact not found.")

    def get_upcoming_birthdays(self):
        today = datetime.now()
        upcoming = []
        for record in self.data.values():
            if record.birthday:
                days = record.days_to_birthday()
                if days is not None and 0 <= days <= 7:
                    next_birthday = today + timedelta(days=days)
                    if next_birthday.weekday() in [5, 6]:
                        next_birthday += timedelta(days=(7 - next_birthday.weekday()))
                    upcoming.append({"name": record.name.value, "birthday": next_birthday.strftime("%d.%m.%Y")})
        return upcoming

    def __str__(self):
        return "\n".join(str(record) for record in self.data.values())

# Functions for serialization/deserialization
def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()  # Return a new address book if the file doesn't exist

# Main application
def main():
    book = load_data()
    print("Welcome to the assistant bot!")

    try:
        while True:
            command = input("Enter a command (add, show, edit, delete, all, birthdays, exit): ")
            if command == "add":
                name = input("Enter name: ")
                phone = input("Enter phone number: ")
                try:
                    record = book.find(name) or Record(name)
                    record.add_phone(phone)
                    book.add_record(record)
                    print(f"Contact {name} added/updated.")
                except ValueError as e:
                    print(e)

            elif command == "show":
                name = input("Enter name: ")
                record = book.find(name)
                if record:
                    print(record)
                else:
                    print("Contact not found.")

            elif command == "edit":
                name = input("Enter name: ")
                old_phone = input("Enter old phone number: ")
                new_phone = input("Enter new phone number: ")
                record = book.find(name)
                if record:
                    try:
                        record.edit_phone(old_phone, new_phone)
                        print("Phone number updated.")
                    except ValueError as e:
                        print(e)
                else:
                    print("Contact not found.")

            elif command == "delete":
                name = input("Enter name: ")
                try:
                    book.delete(name)
                    print(f"Contact {name} deleted.")
                except KeyError as e:
                    print(e)

            elif command == "all":
                print("Address Book:")
                print(book)

            elif command == "birthdays":
                print("Upcoming Birthdays:")
                upcoming = book.get_upcoming_birthdays()
                if not upcoming:
                    print("No upcoming birthdays.")
                else:
                    for entry in upcoming:
                        print(f"{entry['name']}: {entry['birthday']}")

            elif command == "exit":
                print("Goodbye!")
                break

            else:
                print("Unknown command.")
    finally:
        save_data(book)

if __name__ == "__main__":
    main()
