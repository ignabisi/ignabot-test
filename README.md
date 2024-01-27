# Telegram Bot Contact Manager with Docker

## Overview
This Dockerized Telegram Bot Contact Manager simplifies interactions between a Telegram bot and its users. It's perfect for development and debugging, thanks to its Docker integration and local server capabilities.

## Key Features

- **Docker Integration**: Ensures a consistent environment using Docker containers.
- **Local File Storage**: Offers the option to store files locally or in binary format in a database.
- **Cloudflare Tunneling**: Leverages Cloudflare for secure, local tunneling, enhancing debugging and development.
- **API Accessibility**: The API is hosted locally, facilitating easy access and testing.

## Components

1. **TextProcessor**: Manages text message interactions.
2. **PhotoProcessor**: Handles photo processing with face detection features.
3. **VoiceProcessor**: Converts voice messages to a standard audio format and stores them.
4. **ContactManager**: Keeps track of user contacts and manages data within the database.

## Setup and Usage

### Prerequisites
- Docker and Docker Compose installed.
- Cloudflare account for tunneling setup.

### Installation
1. Clone the repository.
2. Navigate to the project directory.
3. Use Docker Compose to build and run the containers.

    ```bash
    docker-compose up --build
    ```

### Usage
- Interact with the Telegram bot by sending text, photo, or voice messages.
- Use the local API for testing and debugging.
- Utilize Cloudflare tunneling for a secure connection to the local server.
