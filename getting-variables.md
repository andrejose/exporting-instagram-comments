# Obtendo os valores para as variáveis *query_hash* and *cookir* 

Inicialmente, acesse o post do Instagram do qual serão extraídos os comentários.

![Instagram post](assets/img/01-more-comments-button.png)

Na página do post, habilite o painel da ferramenta de desenvolvedor no Chrome (F12 para ativar) ou em outro navegador de sua preferência.

Com o painel ativado, selecione a guia Network (Rede) e selecione apenas arquivos vindos de requisição XHR.

![Developer tools](assets/img/02-developer-tools.png)

A partir dessa visualização, clique no botão **+** para carregar mais comentários.

Assim, é realizada uma requisição assíncrona para buscar novos comentários do post. Dentre os parâmetros enviados ao servidor, está nossa primeira variável (*query_hash*):

![Requisição para buscar comentários](assets/img/03-graphql-request.png)

Clicando no arquivo da requisição, dentro da guia Headers, fica fácil copiar o valor dessa variável:

![Copiando query_hash](assets/img/04-query_hash.png)

Ainda na guia Headers, role o conteúdo para baixo até chegar na seção Request Headers:

![Copiando o valor de cookie](assets/img/05-cookie.png)

Nesta área, localize a variável *cookie* e clicando com o botão direito do mouse, clique "Copy value".

**Pronto!** Assim, tem-se os dois valores para extrair os comentários de forma automatizada.