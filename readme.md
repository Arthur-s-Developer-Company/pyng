<img width="333" height="170" alt="ascii-art-pyng" src="ascii-art-pyng.png" />

# O que é?

Pyng é um jogo inspirado no pong, escrito em python com movimentos em 3 dimensões e rastreamento do movimento do mouse, escrito na biblioteca pygame.

# Como instalar:

## Método 1: Baixe o executável

Pegue um executável em [releases](https://github.com/RandomUserjs/pyng/releases/latest)

### Linux:

Torne o arquivo executável:

```bash
chmod +x Pyng-Linux
```

Execute o arquivo:

```bash
./Pyng-Linux
```

### Windows:

Extraia a pasta zipada usando o Winrar ou 7zip, ou o explorer (Windows 11+).

Depois navegue para `./pyng-win/dist/Pyng`, e execute o arquivo `Pyng.exe`

> [!CAUTION]
> Não tire o arquivo da pasta `Pyng`, para que o jogo funcione, suas dependencias se encontram na pasta `_internal`, NÃO A MOVA NEM A EXCLUA!

## Método 2: Compile o código

### Requisitos:

- Python 3.12
- Verifique os requisitos do [Pyinstaller](https://pyinstaller.org/en/stable/requirements.html#requirements) (link)
- Pygame ([Windows](https://www.pygame.org/wiki/GettingStarted#Windows%20installation) | [MacOS](https://www.pygame.org/wiki/GettingStarted#Mac%20installation) | [Linux](https://www.pygame.org/wiki/GettingStarted#Unix%20Binary%20Packages))

Clone o Repositório e entre na pasta dele:

```
git clone https://github.com/RandomUserjs/pyng.git
cd pyng
```

### Linux/MacOS:

Inicie e ative um venv do python:

```bash
python -m venv .venv
source .venv/bin/activate
```

Instale as dependências:

```bash
python -m pip install requirements.txt
```

#### Opção 1: Execute o arquivo python:

```bash
python app.py
```

#### Opção 2: Compile o código

```bash
pyinstaller app.spec
```

Após a compilação, o executável ficará disponível na pasta `./dist/Pyng`

### Windows:

Inicie e ative um venv do python:

```bash
py -m venv .venv
.venv\Scripts\activate
```

Instale as dependências:

```bash
py -m pip install requirements.txt
```

#### Opção 1: Execute o arquivo python:

```bash
py app.py
```

#### Opção 2: Compile o código

```bash
pyinstaller app.spec
```

Após a compilação, o executável ficará disponível na pasta `./dist/Pyng`
