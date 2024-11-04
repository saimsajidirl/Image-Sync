# SRS for Image Sync

1. Introduction
1.1 Purpose

The purpose of this document is to define the functional and non-functional requirements for an image upload and resize service, which allows users to upload images through a web interface. The images are processed and resized in the background using Celery and Redis for task queuing and caching. This document provides a detailed description of the system's behavior, constraints, and architecture.
1.2 Scope

The system enables users to upload images via a web interface, and these images are stored on the server and resized to a specified dimension. Celery tasks handle resizing asynchronously to ensure responsiveness, and Redis is used to cache processed images to prevent duplicate processing. The resized images are stored with a unique hash-based filename to avoid filename conflicts.
1.3 Overview

This system will:

    Allow users to upload up to two images at once.
    Prevent duplicate images from being re-uploaded and re-processed.
    Process images in the background for resizing using a Celery worker.
    Cache the results of resized images in Redis.
    Display uploaded and processed images on the web interface.

2. System Architecture
2.1 System Components

    Django Web Server: Manages the web application, routes requests, and serves HTML templates.
    Celery: Handles asynchronous task processing for image resizing.
    Redis: Used as the broker for Celery and as a cache to store the paths of resized images.
    PostgreSQL/MySQL Database: Stores metadata of uploaded images, including the file name and upload timestamp.

2.2 Data Flow

    Image Upload: Users upload images via a form. Images are saved in the uploaded_images/ directory.
    Celery Task: After an upload, a Celery task resizes the image in the background.
    Redis Cache: The resized image path is cached in Redis using an MD5 hash for quick retrieval.
    Database Storage: Metadata (e.g., file name, upload timestamp, and hash) is saved in the database.

3. Functional Requirements
3.1 User Interface
3.1.1 Image Upload Form

    The form must accept two image files (image1 and image2).
    Only .jpg, .jpeg, and .png file types are supported.

3.2 Image Upload and Storage

    FR-1: The system must save uploaded images in a directory (uploaded_images/) on the server.
    FR-2: The system must check for duplicates by file name. If an image with the same file name exists, it should skip re-uploading.

3.3 Background Image Resizing

    FR-3: Each valid uploaded image should trigger an asynchronous Celery task to resize it to 1920x1080 pixels.
    FR-4: The resizing task should be uniquely identified by an MD5 hash generated from the file contents and name.
    FR-5: The resized image should be stored in the same directory (uploaded_images/) with the filename format <hash>_resized.jpg.

3.4 Caching with Redis

    FR-6: The system must cache the output path of resized images in Redis to prevent duplicate processing.
    FR-7: The system must check the Redis cache before creating a new resizing task.

3.5 Database Management

    FR-8: Store metadata of each uploaded image in a database table, UploadedImage, with fields:
        image (file path),
        uploaded_at (timestamp),
        hash (unique MD5 hash for each image).

3.6 Error Handling and Logging

    FR-9: If an image fails to resize, the Celery task should retry and log the error in a log file.
    FR-10: The system should handle exceptions gracefully and return informative error messages to users (e.g., "Image already exists").

3.7 API Endpoints

    FR-11: Provide a JSON response after an upload, listing successfully uploaded images and their status.

3.8 Display Current Images

    FR-12: Render a list of all previously uploaded images on the web interface.

4. Non-Functional Requirements
4.1 Performance Requirements

    NFR-1: The system should handle up to 100 concurrent image uploads.
    NFR-2: Resizing tasks should complete within 3 seconds on average for a standard 1920x1080 output size.

4.2 Reliability and Availability

    NFR-3: Redis cache must have high availability to support task deduplication and faster processing.
    NFR-4: Celery worker tasks should retry up to three times in case of errors.

4.3 Security

    NFR-5: Ensure file uploads are secure by checking for valid image types and sizes.
    NFR-6: Prevent unauthorized access to the upload page by restricting it to authenticated users.

4.4 Maintainability

    NFR-7: Code should be well-documented and follow PEP 8 guidelines for Python.
    NFR-8: Separate logic into individual functions and classes to ensure modularity.

4.5 Usability

    NFR-9: Users should receive clear feedback on the success or failure of image uploads.

5. System Models
5.1 Database Model

The UploadedImage model will have the following fields:

    image: Path to the uploaded image.
    uploaded_at: Timestamp of the upload.
    hash: Unique hash identifier for deduplication.

5.2 Redis Cache

    Key: MD5 hash of the image file.
    Value: Path to the resized image.
    Expiry: Cache entries can be set to expire if storage becomes an issue.

6. Interface Requirements
6.1 Frontend

    A single HTML template (upload.html) with:
        A file upload form (fields image1 and image2).
        A display area for showing previously uploaded images.

6.2 Backend (Django)

    URL Endpoints:
        /upload-image/: Endpoint for the image upload form.
        POST /upload-image/: Handles form submission and returns a JSON response on success or failure.

7. Constraints
7.1 System Constraints

    The server must have Celery and Redis installed and configured.
    Images are limited in size (suggested: max 5 MB per image).

7.2 Design Constraints

    The system must use Django for the web application framework and Celery for asynchronous task handling.
    Redis should serve both as the Celery broker and caching solution.

8. Assumptions and Dependencies

    Dependencies: Celery, Redis, Pillow, Django.
    Assumptions: Users are authenticated before uploading images.
