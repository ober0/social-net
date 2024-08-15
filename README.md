
---
[README.ru.md](README.ru.md)


# Project Overview

This project is a web application - a social network built with Flask. The application includes features such as user authentication, messaging, notifications, user settings, media management (photos and videos), and tools for handling support requests. The database is managed using SQLAlchemy, while real-time functionality is enabled through Flask-SocketIO.

### Table of Contents
- [Features](#features)
- [Technologies](#technologies)
- [Database Models](#database-models)
- [How to Run](#how-to-run)
- [Project Structure](#project-structure)
- [Additional Information](#additional-information)
- [License](#license)

## Features

### 1. **User Authentication**
   - Authentication logic implemented using cookies and sessions.
   - Support for user login, logout, and authentication status checks.

### 2. **Messaging System**
   - Users can send and receive messages in real-time.
   - Messages are stored in the database; the system supports notifications for new messages.
   - Ability to search and filter chat history.

### 3. **Notifications**
   - Notifications for events like new messages, friend requests, and admin actions.
   - Users can customize their notification preferences in settings.

### 4. **Friends System**
   - Users can send and receive friend requests.
   - Ability to accept, decline, and manage friends.

### 5. **User Profile and Settings**
   - Users can manage their profile information, privacy settings, and notifications.
   - Profiles include data such as avatar, username, and personal information.

### 6. **Media Management**
   - Support for uploading and displaying photos and videos.
   - Users can view their own and others' media galleries.

### 7. **Community Creation and Posts**
   - A button in the main menu to create a community.
   - Ability to edit the community and subscribe to them for news updates.
   - Users can add community posts and receive news from subscribed communities.

### 8. **Like and Comment System**
   - Users can like posts they enjoy.
   - Users can leave comments on posts.

### 9. **Admin Functions**
   - Admins can manage support requests (/admin/support).
   - Tools for user moderation and status changes (admin/change_status).

### 10. **Support and Help**
   - Users can send support requests.
   - Admins can respond to these requests and send notifications.

### And much more!

## Technologies

- **Flask:** Used for routing, template rendering, and request management.
- **SQLAlchemy:** ORM for managing database models and queries.
- **Flask-SocketIO:** Enables real-time messaging and notifications.
- **Flask-Mail:** Allows sending email notifications for support.
- **Jinja2:** Used for rendering HTML templates.
- **Fetch API:** Used for sending asynchronous requests to the server and dynamically loading data.
- **Cookies and Sessions:** For storing client-side information.

## Database Models

The application uses several database models, including:

1. **User**
    - Stores user data, including authentication information (email, password), personal data (name, birth date, gender), as well as profile and privacy settings.
    - Includes fields that allow customizing visibility for certain profile aspects like birth date, gender, city, and education.

2. **Group**
    - Stores information about groups, including their owner, avatar, tag, and subscriber count.

3. **Subscribe**
    - Model for managing user subscriptions to groups, linking user IDs to group IDs.

4. **Friends and FriendRequest**
    - Friends: Stores friendship data between users.
    - FriendRequest: Manages friend requests, including user access information.

5. **Notification**
    - Stores notifications for users, including notification type, text, and date.

6. **Photos and Videos**
    - Manages photo and video uploads, including file name, storage path, and use in posts.

7. **Post**
    - Stores data about user or community posts, including text, images, videos, and the number of likes/comments.

8. **Likes and Comments**
    - Likes: Tracks user likes on posts.
    - Comments: Stores comments left by users under posts.

9. **Setting**
    - Manages user settings like notifications for friend requests, messages, and profile visibility.

10. **TechnicalSupportRequest**
    - Stores user support requests, including subject, description, and status.

11. **Chats and Message**
    - Chats: Manages chats between two users, including the last message and timestamp.
    - Message: Contains individual messages, including sender, recipient, and text.

## How to Run

1. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Up the Database:**
   ```bash
   flask db init
   flask db migrate
   flask db upgrade
   ```

3. **Run the Application:**
   ```bash
   flask run
   ```

4. **Open the Application:**
   Visit `http://127.0.0.1:5000/` in your browser.

## Project Structure

```plaintext
project/
├── app.py
├── config.py
├── models.py
├── smtpData.py
├── templates/
├── static/
│   ├── avatars/
│   ├── css/
│   ├── js/
│   ├── groups/
│   └── users/
└── tests/
```

- **app.py:** The main application file containing routes, logic, and initialization.
- **models.py:** Contains SQLAlchemy models for the database.
- **templates/:** HTML templates for rendering web pages.
- **static/:** Static files (CSS, JS, images, avatars).
- **config.py:** Configuration settings for the application.
- **tests/:** Tests.
- **smtpData.py:** Stores login and password for the SMTP server.

## Additional Information

- The project was fully developed by a single person.
- Development time: 1.5 months.
- Author: Ober0 (Ruslan)  
- [Telegram](https://t.me/Oberrrr)

## License
- <h3>This project is licensed under [MIT License](LICENSE).</h3>
---
