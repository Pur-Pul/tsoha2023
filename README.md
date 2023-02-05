[Project specification](documentation/project_specification.md)

## Installation
Clone this repository and create a .env file in the root directory.

### Contents of .env:
```bash
DATABASE_URL=<tietokannan-paikallinen-osoite>
SECRET_KEY=<salainen-avain>
```

Create the virtual environment with the following command:
```bash
$ python3 -m venv venv
```

### Activate the virtual environment:  
Linux:
```bash
$ source venv/bin/activate
```
Windows command prompt:
```bash
$ venv\Scripts\activate.bat
```
Windows PowerShell:
```bash
$ venv\Scripts\Activate.ps1
```

The following commands should be run in the venv.

Install requirements by running the following command:
```bash
$ pip install -r requirements.txt
```

Start the program using the following command:
```bash
$ invoke start
```

Pylint can be run with the following command:
```bash
$ invoke lint
```

Testing and coverage report:
```bash
$ invoke test
```

## Functionality
The application is a platform for creating and sharing pixel-art.
### Current features
- Password protected accounts.
- Pixel-art editor made in javascript.
- The contents of the editor is actively saved to the database, which means the editor can be closed and resumed at any point.
- Artworks in the editor can be saved to the profile at any point.
- Artworks saved to profile are viewable at the users own profile page.
- Artworks saved to profile can be saved as a post with a freely formulated title in the database. Posts can not yet be viewed.
- When artworks are loaded in on the editor and profiles pages, they are animated to be redrawn in the order the image was drawn, stroke by stroke.
