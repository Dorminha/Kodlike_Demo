# Kodlike

Um jogo simples 2D de ação/aventura desenvolvido com Pygame Zero. Controle um herói, desvie de inimigos e navegue pelo mapa.

## Visão Geral

Kodlike é um jogo roguelike, feito para o desafio prático de python da Kodland.

## Funcionalidades

* Movimentação do Herói: Controle total sobre o personagem principal.
* Animações: Sprites animados para o herói e inimigos (parado e em movimento).
* Inimigos com IA Básica: Inimigos patrulham aleatoriamente e perseguem o jogador quando detectado.
* Mapa em Tiles: O mundo do jogo é construído com tiles de piso e parede.
* Detecção de Colisão: O herói e os inimigos colidem com as paredes.
* Estados de Jogo:
    * Menu Principal (com opções de Iniciar, Música e Sair)
    * Jogando
    * Fim de Jogo (Game Over)
* Música: Música de fundo com controle de ligar/desligar.

## Controles

* **Teclado:**
    * `W`, `S`, `A`, `D` ou **Setas Direcionais**: Mover o herói.
* **Mouse:**
    * Clique nos botões do Menu Principal.
    * Clique na tela de "Fim de Jogo" para retornar ao Menu.

## Requisitos

* Python 3.x
* Pygame Zero

## Como Jogar

1.  **Instale o Python:**
    * Se você ainda não tem o Python instalado, baixe-o em [python.org](https://www.python.org/).

2.  **Instale o Pygame Zero:**
    * Abra o seu terminal ou prompt de comando e digite:
        ```bash
        pip install pgzero
        ```

3.  **Baixe o Código do Jogo:**
    * Clone este repositório ou baixe o arquivo `game.py`.

4.  **Estrutura de Pastas e Assets:**
    * Certifique-se de que o script Python (`game.py`) esteja na pasta raiz do projeto.
    * Crie as seguintes subpastas na mesma pasta do script:
        * `images/`: Para colocar todos os arquivos de imagem (sprites do herói, inimigos, tiles).
        * `music/`: Para colocar o arquivo de música de fundo.

    **Assets Necessários:**

    * **Na pasta `images/`:**
        * `hero_idle_0.png` a `hero_idle_3.png` (sprites do herói parado)
        * `hero_move_0.png` a `hero_move_3.png` (sprites do herói andando)
        * `enemy_idle_0.png` a `enemy_idle_3.png` (sprites do inimigo parado)
        * `enemy_move_0.png` a `enemy_move_3.png` (sprites do inimigo andando)
        * `floor_tile.png` (sprite do tile de chão)
        * `wall_tile.png` (sprite do tile de parede)
        *(Nota: Os nomes dos arquivos de imagem devem corresponder exatamente aos definidos no código.)*

    * **Na pasta `music/`:**
        * `background.ogg` ou `background.mp3` (ou outro formato suportado pelo Pygame). O nome base "background" é usado no código.

5.  **Execute o Jogo:**
    * Navegue até a pasta do projeto no seu terminal ou prompt de comando.
    * Execute o jogo com o seguinte comando:
        ```bash
        pgzrun game.py
        ```

## Licença

Este projeto é de código aberto.
