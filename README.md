What is it all about: 
this is the e-commerce site where user can buy items (both that require shipping and not).
Moreover user may do shopping without any registration (sessions key used). 

![Main page example](mainpage.png "mainpage")

Used technologies:
1. Bootstrap.
2. jQuery ajax.
3. Signals.
4. Selenium (a little).

Coming improvements:
1. Stripe integration.
2. AWS integration.
3. Dockerfile.
4. More tests.
5. Admin panel improvements (customization).

How to run: 
1. Configure your SMPT credentials in .env file in ecommerce folder. 
Required variables:
- EMAIL_HOST_USER=your_email
- EMAIL_HOST_PASSWORD=your_password
2. Run in command line: 

    git clone https://github.com/artemchege/django-ecommerce

3. Then run: 

    python manage.py runserver 
    
4. Or in Docker: 

    later
    
