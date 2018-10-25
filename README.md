# Item Catalog Project


Item Catalog Project, part of the Udacity
[Full Stack Web Developer Nanodegree](https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd004).

## Project purpose
This application provides a database of items within a variety of categories,
and is supported by a user registration and authentication system. Registered 
users have the ability to post, edit and delete their own items.

## Components
- Routing and Templating made with Flask
- Uses SQLAlchemy to communicate with the back-end db
- RESTful API endpoints that return json files
- Uses Google Login to authenticate users
- authenticated users can create edit and delete items
- Front-end forms and webpages built with boostrap

## How to Run the Project

* After installing [Virtual box](https://www.virtualbox.org/wiki/Downloads) and [Vagrant](https://www.vagrantup.com/downloads.html), clone the [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) repository into the text-based interface of your operating system. (e.g. the terminal
window in Linux, the command prompt in Windows)
    ```
    git clone https://github.com/udacity/fullstack-nanodegree-vm.git
    ```
* Clone this repo into catalog directory found in the Vagrant directory

    ```
    git clone https://github.com/manlinar/item-catalog.git
    ```
* Go to item-catalog directory:
    ```
	cd item-catalog
    ```
* Bring up the VM with the following command:

    ```
    vagrant up
    ```

* Then: 
	```
    vagrant ssh
    ```
* and after that:
    ```
    cd /vagrant
    ```
* Add the specific libraries:
    ```
    sudo pip install -r requirements.txt
    ```
* Setup the database:
    ```
    python database_setup.py
    ```
* load some fake information:
    ```
	python fakehotelinfo.py
    ```
* Run the following command:
   ```
   python application.py
   ```
* Open your browser and type:
    ```
    http://localhost:8000/
    ```
 You can now see a Hotel Catalog Application.
 
 ## Helpful Resources

* [Stack Overflow](https://stackoverflow.com/)
* [W3Schools](https://www.w3schools.com/)
* Udacity Student's Forum: [Udacity Forum](https://study-hall.udacity.com/sg-617415-1968/rooms/community:nd004:en-us-general?contextType=room)