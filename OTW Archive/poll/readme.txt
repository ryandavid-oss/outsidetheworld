Advanced Poll v2.03 (PHP)
Copyright (c)2001 Chi Kien Uong
URL: http://www.proxy2.de

Requirements:

  - PHP3 or PHP4

Installation:

1. Upload all php files in ASCII-mode to your server.
   Give write permissions to the webserver on the configuration files.

   polldata                 777 (drwxrwxrwx) (directory)
    - 1                     666 (-rw-rw-rw)
    - 2                     666 (-rw-rw-rw)
    - 3                     666 (-rw-rw-rw)
    - session.php           666 (-rw-rw-rw)
   
   templates                777 (drwxrwxrwx) (directory)
    | default               777 (drwxrwxrwx) (directory)
     - comment.html         666 (-rw-rw-rw)
     - display_foot.html    666 (-rw-rw-rw)
     - display_head.html    666 (-rw-rw-rw)
     - display_loop.html    666 (-rw-rw-rw)
     - result_head.html     666 (-rw-rw-rw)
     - result_foot.html     666 (-rw-rw-rw)
     - result_loop.html     666 (-rw-rw-rw)
    | graphic               777 (drwxrwxrwx) (directory)
     - ...
   
   include                  755 (drwxr-xr-x) (directory)
    - config.inc.php        666 (-rw-rw-rw)

2. Goto the admin page -> http://www.yourdomain.com/poll/admin/

   Username: admin
   Password: poll

   and change the username and password.

