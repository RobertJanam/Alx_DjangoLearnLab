# Permissions and Groups Setup Guide

## TASK 2: Group Configuration

### Step 1: Create Groups
1. Go to Django Admin (/admin)
2. Navigate to "Authentication and Authorization" → "Groups"
3. Create these groups with the following permissions:

### Group 1: Viewers
- Permissions to add: `bookshelf | book | can_view`

### Group 2: Editors
- Permissions to add:
  - `bookshelf | book | can_view`
  - `bookshelf | book | can_create`
  - `bookshelf | book | can_edit`

### Group 3: Admins
- Permissions to add: ALL permissions (or specifically all 4 book permissions)

### Step 2: Assign Users to Groups
1. In Django Admin, go to "Bookshelf" → "Custom users"
2. Edit a user and assign them to appropriate groups

## TASK 4: Testing Permissions

### Test Users Setup:
1. Create test users through Django Admin or registration
2. Assign users to different groups:
   - User A: Viewers group (can only view)
   - User B: Editors group (can view, create, edit)
   - User C: Admins group (full access)

### Expected Behavior:
- **Viewers**: Can only see book list, cannot create/edit/delete
- **Editors**: Can view, create, and edit books, but not delete
- **Admins**: Full CRUD access to books

## Permission Structure:
- `can_view`: Required for viewing book list
- `can_create`: Required for creating new books
- `can_edit`: Required for editing existing books
- `can_delete`: Required for deleting books

## Code Implementation:
- Permissions are defined in `Book.Meta.permissions`
- Views are protected using `@permission_required` decorators
- Templates check permissions using `{{ perms.app_name.permission_name }}`