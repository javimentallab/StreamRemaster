# Política de privacidade — StreamRemaster

*Última atualização: 19 de novembro de 2026*

*[English](PRIVACY.md) · [Español](PRIVACY.es.md) · [Deutsch](PRIVACY.de.md) · [Français](PRIVACY.fr.md) · [Italiano](PRIVACY.it.md) · [Nederlands](PRIVACY.nl.md) · [Polski](PRIVACY.pl.md) · [Português](PRIVACY.pt.md) · [Русский](PRIVACY.ru.md) · [Українська](PRIVACY.uk.md) · [简体中文](PRIVACY.zh-CN.md) · [日本語](PRIVACY.ja.md) · [한국어](PRIVACY.ko.md) · [ไทย](PRIVACY.th.md) · [हिन्दी](PRIVACY.hi.md) · [Català](PRIVACY.ca.md) · [Galego](PRIVACY.gl.md) · [Euskara](PRIVACY.eu.md)*

## 1. Controlador dos dados

A extensão de navegador StreamRemaster, anteriormente denominada Stream Transcription (a “Extensão”), é publicada em addons.mozilla.org e em https://github.com/javimentallab/StreamRemaster por Javier Comyn Pérez, com endereço na calle Olivos, número 36, 28670 Villaviciosa de Odón, Madrid, España (o “Fornecedor”), sob o nome de desenvolvedor javimentallab. O Fornecedor é o controlador dos dados pessoais a que se refere esta política, que é regida pelo Regulamento (UE) 2016/679, Regulamento Geral sobre a Proteção de Dados (o “RGPD”), e pela Lei Orgânica espanhola 3/2018, de 5 de dezembro, de Proteção de Dados Pessoais e garantia dos direitos digitais (Ley Orgánica 3/2018, de 5 de diciembre, de Protección de Datos Personales y garantía de los derechos digitales). O usuário da Extensão (o “Usuário”) pode entrar em contato com o Fornecedor pelo e-mail jotacomyn@gmail.com.

## 2. Inexistência de tratamento de dados pessoais na Extensão

A Extensão não coleta nem trata dados pessoais do Usuário em nome do Fornecedor. A Extensão não possui contas de usuário, publicidade, ferramentas de análise nem sistemas de relatório de falhas, e não se comunica com nenhum servidor do Fornecedor; não inclui nem incluirá nenhum desses elementos. Nenhum dado do Usuário, nem o áudio nem as imagens processados pela Extensão, chega ao Fornecedor. Os únicos dados pessoais que o Fornecedor pode vir a tratar são aqueles que o Usuário lhe fornecer por iniciativa própria ao entrar em contato com ele, nos termos da seção 7.

## 3. Funcionamento da Extensão

**3.1. Legendas com um servidor do Usuário.** Quando o Usuário ativa as legendas no modo servidor, a Extensão envia o áudio da aba para o endereço de servidor que o próprio Usuário inseriu na Extensão, normalmente um servidor WhisperLive instalado no computador ou na rede local do Usuário, e recebe dele as legendas. Esse servidor é instalado e controlado pelo Usuário, que é o único responsável por sua configuração e por sua segurança; o Fornecedor não tem acesso a ele nem ao áudio.

**3.2. Legendas no computador do Usuário.** Quando o Usuário opta por transcrever no computador, o áudio é processado no navegador, na placa de vídeo do Usuário, e não sai do computador.

**3.3. Vídeo fluido.** A função de vídeo fluido processa as imagens do vídeo da página no navegador, na placa de vídeo do Usuário. As imagens não saem do computador nem são armazenadas.

## 4. Comunicações com terceiros

A Extensão somente se conecta a sites diferentes do servidor do Usuário quando este o solicita expressamente, e apenas nas seguintes hipóteses:

- **GitHub (api.github.com).** Somente quando o Usuário clica em “Procurar atualizações”, a Extensão solicita ao GitHub o número da versão mais recente publicada. A solicitação não contém dados sobre o Usuário nem sobre o uso que ele faz da Extensão.
- **Hugging Face (huggingface.co).** Somente quando o Usuário baixa um modelo de transcrição para usá-lo no computador, a Extensão o baixa do Hugging Face.
- **Endereços informados pelo Usuário.** Quando o Usuário adiciona um modelo de vídeo fluido informando seu endereço, a Extensão o baixa desse endereço.

Como em qualquer conexão à Internet, o site ao qual a Extensão se conecta recebe o endereço IP do Usuário e a identificação do seu navegador. Cada um desses sites trata esses dados na qualidade de controlador, de acordo com sua própria política de privacidade, pela qual o Fornecedor não se responsabiliza.

## 5. Permissões

- **Armazenamento (storage):** guardar as configurações da Extensão no navegador.
- **Captura da aba (tabCapture e offscreen), somente em navegadores baseados no Chromium:** obter o áudio da aba em que o Usuário ativa as legendas, somente depois que o Usuário clicar no botão da Extensão nessa aba.
- **Aba ativa e execução de scripts (activeTab e scripting), somente em navegadores baseados no Chromium:** exibir as legendas e aplicar o vídeo fluido na aba em que o Usuário clicou no botão da Extensão.
- **Acesso a sites (<all_urls>):** no Firefox, ler o áudio e o vídeo da página para as legendas e o vídeo fluido. Em navegadores baseados no Chromium, é uma permissão opcional, que a Extensão só solicita se o Usuário marcar a caixa que ativa automaticamente o vídeo fluido em qualquer site.

## 6. Dados armazenados no navegador

A Extensão guarda no armazenamento do navegador do Usuário suas configurações (endereço do servidor, modelo, idiomas, tamanho e posição das legendas e opções do vídeo fluido), os modelos de vídeo fluido que o Usuário adicionar e os modelos de transcrição que o Usuário baixar para usá-los no computador. Esses dados permanecem no navegador do Usuário, não são enviados ao Fornecedor e são excluídos quando a Extensão é desinstalada; os modelos também podem ser excluídos nas configurações da Extensão. Se o Usuário ativar a opção de salvar as legendas, ao interrompê-las é baixado para o computador do Usuário um arquivo `.srt`, que fica à disposição do Usuário.

## 7. Dados das comunicações do Usuário

Quando o Usuário entra em contato com o Fornecedor por e-mail, o Fornecedor trata o endereço de e-mail do Usuário, seu nome, se informado, e o conteúdo da mensagem. Quando o Usuário registra uma ocorrência (issue) no GitHub, essa ocorrência é pública e está sujeita aos termos e à política de privacidade do GitHub.

Nos termos do artigo 13.º do RGPD, são prestadas as seguintes informações:

- **Finalidade:** atender à consulta, à ocorrência ou à solicitação do Usuário.
- **Base legal:** o consentimento do Usuário, manifestado ao entrar em contato com o Fornecedor [artigo 6.º, n.º 1, alínea a), do RGPD], e, no exercício dos direitos previstos na seção 8, o cumprimento de obrigação legal do Fornecedor [artigo 6.º, n.º 1, alínea c), do RGPD].
- **Prazo de conservação:** o tempo necessário para atender à comunicação e, em seguida, o prazo de prescrição das ações que dela possam decorrer. Decorrido esse prazo, os dados são excluídos.
- **Destinatários:** os dados não são compartilhados com terceiros, salvo por obrigação legal. O serviço de e-mail do Fornecedor é prestado pelo Google, na qualidade de provedor de serviço.

## 8. Direitos do Usuário

O Usuário pode exercer os direitos de acesso, retificação, eliminação, limitação do tratamento, oposição e portabilidade, nos termos dos artigos 15.º a 22.º do RGPD, bem como revogar a qualquer momento o consentimento dado, sem que isso afete a licitude do tratamento realizado antes da revogação, entrando em contato com o Fornecedor pelo e-mail jotacomyn@gmail.com. O Usuário também pode apresentar reclamação à Agencia Española de Protección de Datos (Agência Espanhola de Proteção de Dados, www.aepd.es).

## 9. Alterações

O Fornecedor poderá alterar esta política; a data da última atualização constará no início deste documento.

## 10. Contato

As dúvidas relativas a esta política poderão ser encaminhadas ao Fornecedor pelo e-mail jotacomyn@gmail.com ou mediante o registro de uma ocorrência em https://github.com/javimentallab/StreamRemaster/issues.
