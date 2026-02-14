# Blog Post Management Features

## Overview
The blog post management system provides full CRUD (Create, Read, Update, Delete) functionality for blog posts. Authors can create, edit, and delete their own posts, while all users (authenticated or not) can view posts.

## Features

### 1. List Posts (/posts/)
- Displays all blog posts in a grid layout
- Shows post title, author, publication date, and content preview
- Pagination for better performance with many posts
- Each post card includes:
  - Title (clickable to view full post)
  - Author name
  - Publication date
  - Content excerpt (first 50 words)
  - "Read More" link
  - Edit/Delete buttons for post authors

### 2. View Post (/post/<id>/)
- Shows complete blog post with full content
- Displays author information and publication date
- Edit/Delete buttons for post authors
- Navigation back to post list

### 3. Create Post (/post/new/)
- Form for creating new blog posts
- Requires authentication
- Fields:
  - Title (required, minimum 5 characters)
  - Content (required, minimum 20 characters)
- Automatically sets author to logged-in user
- Success message after creation

### 4. Edit Post (/post/<id>/edit/)
- Form pre-filled with existing post data
- Only accessible to post author
- Same validation as create form
- Success message after update

### 5. Delete Post (/post/<id>/delete/)
- Confirmation page before deletion
- Only accessible to post author
- Shows post title for confirmation
- Warning about permanent deletion
- Success message after deletion

## Permissions

| Action | Anonymous User | Authenticated User | Post Author |
|--------|---------------|-------------------|-------------|
| View Post List | ✓ | ✓ | ✓ |
| View Post Detail | ✓ | ✓ | ✓ |
| Create Post | ✗ | ✓ | - |
| Edit Post | ✗ | ✗ | ✓ |
| Delete Post | ✗ | ✗ | ✓ |

## URL Patterns

| URL | View Name | Method | Description |
|-----|-----------|--------|-------------|
| `/posts/` | `post-list` | GET | List all posts |
| `/post/new/` | `post-create` | GET/POST | Create new post |
| `/post/<int:pk>/` | `post-detail` | GET | View single post |
| `/post/<int:pk>/edit/` | `post-update` | GET/POST | Edit post |
| `/post/<int:pk>/delete/` | `post-delete` | GET/POST | Delete post |

## Testing Instructions

### Test Post Creation
1. Login to the application
2. Click "Create New Post" button
3. Fill in title and content
4. Submit form
5. Verify redirect to post list with success message
6. Verify new post appears in list

### Test Post Editing
1. Navigate to your post
2. Click "Edit" button
3. Modify content
4. Submit form
5. Verify changes saved with success message

### Test Post Deletion
1. Navigate to your post
2. Click "Delete" button
3. Confirm deletion
4. Verify post removed with success message

### Test Permissions
1. Try accessing edit URL of another user's post
2. Verify 403 Forbidden response
3. Try creating post while logged out
4. Verify redirect to login page

## Security Features
- CSRF protection on all forms
- LoginRequiredMixin for create/update/delete
- UserPassesTestMixin for edit/delete (author only)
- Form validation for data integrity
- Safe deletion with confirmation
- Proper error handling and user feedback