# Changelog

Informações sobre atualizações no projeto serão registradas aqui.

## [Unreleased]
### Adicionado
+ Criação de morador possui um novo passo requerindo um áudio dele dizendo o próprio nome
+  Configurado path e rede interna no docker-compose para subir a aplicação localmente
+  Novo comando para enviar feedbacks sobre o sistema.
+  Interação de visitante para solicitar uma entrada.
+  Interação do morador para lidar com a entrada do visitante.
+ Criação de um sistema de notificação para administradores, que recebe uma mensagem para aprovar ou rejeitar o cadastro de um morador.

### Alterado
+ mudança do docker alpine para debian slim
+ A api é acessada agora via registry do projeto em suas versões de homologação e deploy
+ O tratamento de áudio agora é delegado à API

### Removido
+ Manipulações de MFCC removidas do código

#### Melhorias
+ Agora as bibliotecas de processamento de sinais estão devidamentes instaladas

## Release 1 - 10 Outubro de 2019

Em: https://github.com/fga-eps-mds/2019.2-Alohomora/releases

 ---
 Modelo padrão do changelog disponível [aqui](https://keepachangelog.com/en/0.3.0/).

