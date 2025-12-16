# Admin User Management Scripts

**Radhe Radhe! 🙏**

## Create Admin User

### Interactive Mode
```bash
cd backend
source venv/bin/activate
python scripts/create_admin.py
```

The script will prompt you for:
- Email address
- Name
- Mobile number (optional, 10 digits)

### Command Line Mode
```bash
cd backend
source venv/bin/activate
python scripts/create_admin.py --email admin@example.com --name "Admin User" --mobile "9876543210"
```

### Options
- `--email`: Admin email address (required)
- `--name`: Admin name (required)
- `--mobile`: Mobile number, 10 digits (optional)

## Example

```bash
python scripts/create_admin.py --email admin@lifeschool.com --name "Admin User" --mobile "9876543210"
```

## Notes

- If a user with the email already exists, the script will ask if you want to update their role to ADMIN
- Mobile number is optional but recommended for profile completion
- After creating the admin user, login through the normal login flow (`/auth/google`) to get a JWT token

## Login as Admin

1. Go to the frontend login page
2. Enter the admin email and name
3. You'll receive a JWT token with ADMIN role
4. You can now create exams and access all admin features

**Radhe Radhe! 🙏**


