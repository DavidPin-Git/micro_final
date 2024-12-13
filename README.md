# Musica para surdos
Uma ferramenta para pessoas com deficiencia auditiva sentirem a musica.
O projeto consiste na percepção tatil e visual da musica, atraves de vibração e um visualizer.

## Instalação

1. Clone o repositório.
2. Baixe a ferramenta ffmpeg
3. Extraia e adiciona a basta ffmpeg/bin ao PATH
4. Certifique-se de estar utilizando a versão 3.10 do Python
5. Instale as dependencias:
   pip install -r requirements.txt

## Uso

0. Execute Tkinter_GUI.py
1. Selecione as faixas que deseja tocar (se nenhuma for selecionada, é reproduzida a musica na integra) e o volume
2. Carregue a musica arratando para a area de carregamento ou clique em carregar e abra a musica. Espere alguns segundos.
3. Depois de carregado, voce pode reproduzir e pausar a musica a qualquer momento. A reprodução não é instantanea, mas não demora.

## Como funciona

### Resumo
Ao carregar a musica é feita a separação das faixas, a partir da biblioteca Spleeter, as faixas são mandadas para o pre processamento e depois de terminado está pronta para ser reproduzida.

- Spleeter:
É utilizado IA para isolar as faixas de um audio a partir de frequencias determinadas.
Optamos por dividir nas 5 faixas possiveis: vocais, baixo, piano, bateria e 'outros', após serem usoladas é criado um arquivo de audio .wav para cada uma das faixas na pasta output/"nome do audio"/.

- Pre Processamento:
Analisa as frequencias do audio recebido e separa em 3 intervalos, graves, medios e agudos.
É gerado um arquivo json com todas essas informações, para posteriomente ser lido pela função de reprodução.

- Reprodução:
É criado um vetor para cada informação do arquivo json.
O audio é reproduzido por um player e em paralelo uma função de callback e frequentimente chamada.
A função de callback lê as informações de cada vetor de forma iterativa e seguindo o tempo da musica, a função também manda de forma codificada instruções para os motores de vibração e o visualizer conforme as informações lidas.
