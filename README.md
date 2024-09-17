# AI-Powered Adaptive Learning Platform

This project is an AI-powered adaptive learning platform using Flask and Vanilla JS with personalized content delivery. It now includes Progressive Web App (PWA) features for offline learning capabilities on mobile devices.

## Features

- User authentication and authorization
- Personalized course recommendations
- Adaptive learning paths
- Interactive quizzes
- Peer-to-peer learning with study groups and forums
- Progressive Web App (PWA) for offline learning
- Mobile-friendly responsive design

## Offline Capabilities

The platform now supports offline learning through the following features:

- Service Worker for caching static assets and API responses
- IndexedDB for storing course content and user progress
- Offline-first approach for course viewing and quiz taking
- Automatic synchronization of offline data when the user comes back online

## Setup and Installation

1. Clone the repository
2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up the database:
   ```
   flask db upgrade
   ```
4. Run the development server:
   ```
   python main.py
   ```

## Usage

1. Open the application in a web browser or on a mobile device
2. Register for an account or log in
3. Browse available courses and start learning
4. Access course content offline by saving it for offline use
5. Take quizzes and track your progress
6. Participate in study groups and forum discussions

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.
