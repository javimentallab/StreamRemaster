# Translations beyond English and Spanish, read by tools/i18n-messages.py.
# One "key|text" per line; {0}, {1}… are placeholders and must match the English text.
# Model names, "WhisperLive", "Hugging Face", "VRAM", "int8", "faster-whisper", ".srt" stay as they are.

LANGS = {}

LANGS['pt_BR'] = """
error_local_lost|A placa de vídeo parou o modelo de transcrição várias vezes seguidas.
fg_hq_badge|Para placas de vídeo potentes
where_fg_models|Onde ficam os modelos
fg_local_title|Modelos de vídeo fluido neste computador
fg_server_title|Modelos de vídeo fluido no servidor
fg_server_intro|O servidor só os guarda: o modelo escolhido é baixado dele e roda na placa de vídeo deste computador.
fg_server_none|O servidor ainda não tem modelos de vídeo fluido.
fg_server_old|Este servidor não guarda modelos de vídeo fluido: atualize-o para a versão mais recente.
fg_add_server_title|Adicionar ao servidor
fg_server_loading|Baixando o modelo do servidor…
section_transcription|Modelos de transcrição
transcription_intro|Escolha onde a fala vira texto: em um servidor WhisperLive ou na placa de vídeo deste computador.
where_transcribe|Onde transcrever
engine_server|No servidor
engine_local|Neste computador
trans_server_title|Modelos de transcrição no servidor
trans_local_title|Modelos de transcrição neste computador
badge_in_use|Em uso
fg_downloaded_title|Baixados
fg_add_title|Adicionar um modelo
fg_add_url_placeholder|Endereço de um arquivo de modelo (.stmodel)
fg_download_failed|Não foi possível baixar ({0}). Baixe o arquivo pelo navegador e escolha-o neste computador.
fg_memory|Memória de vídeo: cerca de {0} com um vídeo 1080p
fg_memory_4k|cerca de {0} ampliando de 1080p para 4K
fg_memory_now|Memória de vídeo em uso: cerca de {0}
fg_file_size|Arquivo: {0}
fg_options|Opções
fg_sharpen|Nitidez
fg_sharpen_off|Desativada
fg_sharpen_soft|Suave
fg_sharpen_medium|Média
fg_sharpen_strong|Forte
fg_resolution|Resolução de destino da ampliação
fg_res_original|Original (sem ampliar)
fg_model|Modelo de vídeo fluido
fg_kind_sr|Só ampliação
fg_kind_fi|Só quadros intermediários
fg_builtin|Incluído
fg_model_none|Nenhum (sem IA)
section_fgmodels|Modelos de vídeo fluido
fg_models_hint|O vídeo fluido sempre roda na placa de vídeo deste computador. O StreamRemaster vem com a extensão; outros modelos podem ficar neste computador ou no seu servidor.
fg_add_model|Escolher um arquivo neste computador
fg_no_models|Nenhum modelo baixado ainda.
fg_model_bad|Esse arquivo não é um modelo válido.
tab_subs|Legendas
tab_fg|Vídeo fluido
fg_start|Ativar vídeo fluido
fg_stop|Desativar vídeo fluido
fg_target|FPS desejado
fg_target_display|Igual à tela
fg_state_off|Desligado
fg_state_measuring|Medindo o vídeo…
fg_state_on|{0} fps (vídeo a {1} fps)
fg_no_video|Não há nenhum vídeo em reprodução nesta página.
fg_no_webgpu|Este navegador não pode usar a GPU para isto (WebGPU não está disponível).
fg_cannot_read|Este vídeo não pode ser lido: está protegido ou vem de outro site.
fg_unavailable|Esta página não permite extensões.
fg_auto_start|Ativar o vídeo fluido ao reproduzir um vídeo
subs_auto_start|Iniciar as legendas ao reproduzir um vídeo
auto_start_hint|Neste navegador, só funciona nas abas em que você clicou no botão da extensão, até que mudem para outro site.
fg_allow_all_sites|Permitir em todos os sites
extName|StreamRemaster
extDescription|Legendas ao vivo para qualquer aba, transcritas e traduzidas pelo seu próprio servidor Whisper.
start|Ativar legendas
stop|Desativar legendas
status_idle|Pronto
status_connecting|Conectando…
status_loading|Carregando o modelo…
status_listening|Ouvindo…
status_live|Ao vivo
status_stalled|Áudio parado
status_error|Erro
status_noresponse|Sem resposta
model|Modelo de transcrição
model_server_default|O do servidor
model_default_tag|{0} · padrão
manage_models|Gerenciar modelos
spoken_lang|Idioma do áudio
auto_detect|Automático
detected|Detectado: {0}
subs_lang|Legendas em
original_lang|Sem tradução
lines|Linhas
text_size|Tamanho do texto
save_srt|Salvar as legendas (.srt) ao parar
advanced|Avançado
use_vad|Pular silêncios (detecção de voz)
settings|Configurações
first_load_hint|Na primeira vez, um modelo pode levar até um minuto para carregar.
options_locked|Desative as legendas para mudar estas opções.
server_setup_title|Conecte seu servidor
server_setup_hint|O StreamRemaster transcreve com um servidor WhisperLive no seu computador ou na sua rede, ou com a placa de vídeo deste computador.
server_address|Endereço do servidor
server_placeholder|ex.: localhost:9090 ou 192.168.1.10:9090
connect|Conectar
server_ok_models|Conectado · {0} modelos
server_ok_one_model|Conectado · 1 modelo
server_plain|Conectado · WhisperLive padrão (sem gerenciamento de modelos)
server_checking|Verificando…
server_unreachable|Não foi possível conectar ao servidor. Ele está ligado? Verifique o endereço e o firewall.
server_timeout|O servidor não respondeu a tempo.
server_bad_url|Esse endereço não é válido.
server_change|Alterar
server_help|Como monto um servidor?
server_help_1|Você precisa de um servidor WhisperLive (livre e gratuito) rodando em um computador, de preferência com placa de vídeo NVIDIA. Modelos pequenos também funcionam só com o processador.
server_help_2|Depois digite aqui o endereço dele: o IP do computador e a porta, ex.: 192.168.1.10:9090. Se estiver neste mesmo computador, localhost:9090.
server_help_3|Para baixar e gerenciar modelos por esta página, adicione ao servidor o complemento do StreamRemaster.
server_help_guide|Guia passo a passo
error_capture|Esta aba não pode ser capturada (páginas do navegador, lojas de extensões e PDFs não são permitidos).
error_no_media|Não há vídeo nem áudio nesta página.
error_server_full|O servidor está ocupado. Espera estimada: {0} min.
error_disconnected|O servidor fechou a conexão.
error_model_load|⚠ Não há memória de vídeo (VRAM) suficiente no servidor para este modelo. Escolha um modelo menor ou ative “Economizar memória (int8)” em Avançado.
warn_no_response|⚠ As legendas pararam de chegar, embora haja som. Provavelmente o modelo não cabe na memória de vídeo (VRAM) do servidor: escolha um modelo menor ou ative “Economizar memória (int8)” em Avançado.
warn_slow_load|⚠ O modelo está demorando demais para carregar. Pode não caber na memória de vídeo (VRAM) do servidor: escolha um modelo menor ou ative “Economizar memória (int8)” em Avançado.
error_reload|Recarregue a página (F5) e comece de novo.
error_no_server|Primeiro configure o servidor.
settings_title|StreamRemaster · Configurações
section_subtitles|Legendas
section_interface|Interface
section_about|Sobre
installed_models|Instalados no servidor
no_models|Ainda não há modelos instalados.
badge_default|Padrão
badge_loaded|Na memória
badge_selected|Escolhido
use_model|Usar
delete_model|Apagar
confirm_delete|Apagar {0} do servidor? Libera {1}.
add_model|Adicionar um modelo
add_model_hint|Cole o nome ou o link de um modelo do Hugging Face. Serve qualquer modelo Whisper: os do faster-whisper (CTranslate2) são usados como estão e os normais (transformers) são convertidos sozinhos. Um link direto para um .zip ou .tar.gz com um modelo também serve.
add_model_placeholder|ex.: Systran/faster-whisper-large-v3
download|Baixar
suggestions|Sugestões:
browse_hf|Ver modelos Whisper no Hugging Face
vram_hint|Modelos maiores acertam mais, mas pedem mais memória da placa de vídeo: small ≈ 1 GB, medium ≈ 2 GB, large ≈ 4 GB.
keep_open|Deixe esta página aberta até o download terminar.
job_downloading|Baixando… {0} de {1}
job_downloading_nosize|Baixando… {0}
job_converting|Convertendo para o formato faster-whisper…
job_extracting|Descompactando…
job_ready|Instalado
job_error|Falhou: {0}
retry|Tentar de novo
plain_server_hint|É um servidor WhisperLive padrão: digite um tamanho de modelo (tiny, base, small, medium, large-v3, large-v3-turbo) e o servidor o baixa na primeira vez. Para baixar qualquer modelo por aqui, instale no servidor o complemento do StreamRemaster.
model_name|Nome do modelo
save|Salvar
saved|Salvo
reset_position|Reposicionar as legendas
position_reset_done|Pronto: elas voltarão para baixo.
section_performance|Desempenho
performance_hint|Se a placa de vídeo do servidor ficar sem memória (legendas que não chegam ou um aviso de memória), estas duas opções liberam bastante. Só funcionam com o servidor do StreamRemaster.
precision|Precisão do modelo
precision_auto|Automática
precision_int8|Economizar memória (int8)
precision_hint|int8 usa cerca de metade da memória de vídeo e, na prática, escreve o mesmo texto.
translator_device|O tradutor roda na
device_gpu|Placa de vídeo
device_cpu|Processador (CPU)
translator_device_hint|No processador libera memória de vídeo, mas as legendas traduzidas chegam um pouco mais tarde.
interface_lang|Idioma da interface
lang_auto|O do navegador
about_text|Código-fonte disponível (licença PolyForm Noncommercial). O áudio só vai para o servidor que você configurar aqui; nada é enviado para nenhum outro lugar.
about_based|Baseado no WhisperLive, da Collabora.
source_code|Código-fonte
subtitle_preview|É assim que suas legendas vão ficar.
err_invalid_source|Isso não é um nome de modelo do Hugging Face nem um link.
err_unsupported_url|Só links do Hugging Face ou links diretos para arquivos .zip / .tar.gz.
err_repo_not_found|Esse modelo não existe no Hugging Face (confira o nome).
err_gated_repo|Esse modelo pede para aceitar os termos no Hugging Face; o servidor precisa de um HF_TOKEN.
err_not_whisper|Isso não é um modelo Whisper.
err_no_weights|Esse repositório não tem os pesos do modelo.
err_network_error|Erro de rede. Tente de novo: continua de onde parou.
err_download_failed|O download falhou.
err_convert_failed|Não foi possível converter o modelo.
err_bad_archive|O arquivo compactado está danificado ou não é seguro.
err_already_downloading|Já está sendo baixado.
err_already_installed|Já está instalado.
err_management_disabled|O gerenciamento de modelos está desativado neste servidor.
err_is_default|É o modelo padrão do servidor; não pode ser apagado daqui.
err_in_use|Uma transcrição em andamento está usando ele.
err_not_found|Esse modelo não está mais no servidor.
err_server_error|Erro do servidor.
err_unreachable|Não foi possível conectar ao servidor.
err_timeout|O servidor não respondeu a tempo.
err_unknown|Erro inesperado ({0}).
updates|Atualizações
check_updates|Procurar atualizações
check_again|Procurar de novo
update_now|Atualizar
update_available|A versão {0} já está disponível (você tem a {1}).
update_latest|Você tem a versão mais recente ({0}).
update_rate_limited|O GitHub está limitando as consultas por um tempo. Tente de novo mais tarde.
update_failed|Não foi possível procurar atualizações. Verifique a conexão e tente de novo.
update_how_firefox|O Firefox instala as versões novas sozinho. Para tê-la agora, abra about:addons, clique no ícone de engrenagem e escolha “Procurar atualizações”. Uma versão recém-lançada pode levar alguns dias para chegar ao site de extensões.
update_how_chromium|Para atualizar, baixe o zip do Chromium na página da versão, descompacte por cima da pasta antiga e clique no ícone de recarregar no cartão do StreamRemaster em chrome://extensions. Suas configurações são mantidas.
update_privacy|Ao procurar, só se pergunta ao GitHub o número da versão mais recente; nada mais é enviado.
server_update_available|Seu servidor tem a versão {0} e a {1} já está disponível. Para atualizá-lo, execute isto no computador onde ele roda:
server_version_unknown|Seu servidor não informa a versão, então é anterior a esta verificação. Para atualizá-lo, execute isto no computador onde ele roda:
server_update_latest|Seu servidor está atualizado ({0}).
server_update_note|Os modelos ficam no volume do Docker e não são baixados de novo. Se você alterou o docker-compose.yml e o git pull reclamar, execute git stash antes e git stash pop depois.
setup_or|ou
use_local|Usar este computador
use_local_hint|O Whisper roda na placa de vídeo deste computador, sem servidor. O modelo é baixado uma vez, nas Configurações.
local_footer|Este computador
local_none|Nenhum modelo: baixe um
local_intro|O Whisper roda no navegador, na sua placa de vídeo (WebGPU). Cada modelo é baixado uma vez do Hugging Face e fica no navegador. Os maiores escrevem melhor e precisam de mais memória de vídeo.
local_sizes|Download {0} · ocupa {1} · cerca de {2} de memória de vídeo
local_progress|Baixando… {0} de {1}
local_cancel|Cancelar
local_gpu|Placa de vídeo: {0}
badge_downloaded|Baixado
error_no_webgpu|Este navegador não consegue usar a placa de vídeo (WebGPU), então não pode transcrever neste computador.
error_local_missing|Baixe um modelo primeiro, em Configurações → Modelos neste computador.
error_local_failed|A transcrição neste computador parou por causa de um erro.
error_local_vram|⚠ Não há memória de vídeo suficiente neste computador para este modelo. Escolha um menor.
local_download_failed|O download falhou ({0}).
local_confirm_delete|Apagar o modelo {0} deste computador? Libera {1}.
local_only_english|Neste computador as legendas só podem ser traduzidas para o inglês.
"""

LANGS['fr'] = """
error_local_lost|La carte graphique a arrêté le modèle de transcription plusieurs fois de suite.
fg_hq_badge|Pour cartes graphiques puissantes
where_fg_models|Où sont les modèles
fg_local_title|Modèles de vidéo fluide sur cet ordinateur
fg_server_title|Modèles de vidéo fluide sur le serveur
fg_server_intro|Le serveur ne fait que les garder : le modèle choisi en est téléchargé et fonctionne sur la carte graphique de cet ordinateur.
fg_server_none|Le serveur n’a encore aucun modèle de vidéo fluide.
fg_server_old|Ce serveur ne garde pas de modèles de vidéo fluide : mettez-le à jour vers la dernière version.
fg_add_server_title|Ajouter au serveur
fg_server_loading|Téléchargement du modèle depuis le serveur…
section_transcription|Modèles de transcription
transcription_intro|Choisissez où la parole devient du texte : sur un serveur WhisperLive ou sur la carte graphique de cet ordinateur.
where_transcribe|Où transcrire
engine_server|Sur le serveur
engine_local|Sur cet ordinateur
trans_server_title|Modèles de transcription sur le serveur
trans_local_title|Modèles de transcription sur cet ordinateur
badge_in_use|Utilisé
fg_downloaded_title|Téléchargés
fg_add_title|Ajouter un modèle
fg_add_url_placeholder|Adresse d’un fichier de modèle (.stmodel)
fg_download_failed|Impossible de le télécharger ({0}). Téléchargez le fichier avec le navigateur et choisissez-le sur cet ordinateur.
fg_memory|Mémoire graphique : environ {0} avec une vidéo 1080p
fg_memory_4k|environ {0} en agrandissant de 1080p à 4K
fg_memory_now|Mémoire graphique utilisée : environ {0}
fg_file_size|Fichier : {0}
fg_options|Options
fg_sharpen|Netteté
fg_sharpen_off|Désactivée
fg_sharpen_soft|Douce
fg_sharpen_medium|Moyenne
fg_sharpen_strong|Forte
fg_resolution|Résolution cible de l'agrandissement
fg_res_original|Originale (sans agrandissement)
fg_model|Modèle de vidéo fluide
fg_kind_sr|Agrandissement seulement
fg_kind_fi|Images intermédiaires seulement
fg_builtin|Intégré
fg_model_none|Aucun (sans IA)
section_fgmodels|Modèles de vidéo fluide
fg_models_hint|La vidéo fluide fonctionne toujours sur la carte graphique de cet ordinateur. StreamRemaster est fourni avec l’extension ; d’autres modèles peuvent être sur cet ordinateur ou sur votre serveur.
fg_add_model|Choisir un fichier sur cet ordinateur
fg_no_models|Aucun modèle téléchargé pour l’instant.
fg_model_bad|Ce fichier n'est pas un modèle valide.
tab_subs|Sous-titres
tab_fg|Vidéo fluide
fg_start|Activer la vidéo fluide
fg_stop|Désactiver la vidéo fluide
fg_target|FPS cible
fg_target_display|Comme l'écran
fg_state_off|Désactivé
fg_state_measuring|Mesure de la vidéo…
fg_state_on|{0} fps (vidéo à {1} fps)
fg_no_video|Aucune vidéo n'est en cours de lecture sur cette page.
fg_no_webgpu|Ce navigateur ne peut pas utiliser la carte graphique pour cela (WebGPU n'est pas disponible).
fg_cannot_read|Cette vidéo ne peut pas être lue : elle est protégée ou provient d'un autre site.
fg_unavailable|Cette page n'autorise pas les extensions.
fg_auto_start|Activer la vidéo fluide à la lecture d'une vidéo
subs_auto_start|Lancer les sous-titres à la lecture d'une vidéo
auto_start_hint|Dans ce navigateur, cela ne fonctionne que dans les onglets où vous avez cliqué sur le bouton de l'extension, jusqu'à ce qu'ils changent de site.
fg_allow_all_sites|Autoriser sur tous les sites
extName|StreamRemaster
extDescription|Sous-titres en direct pour n’importe quel onglet, transcrits et traduits par votre propre serveur Whisper.
start|Activer les sous-titres
stop|Arrêter les sous-titres
status_idle|Prêt
status_connecting|Connexion…
status_loading|Chargement du modèle…
status_listening|Écoute…
status_live|En direct
status_stalled|Audio arrêté
status_error|Erreur
status_noresponse|Pas de réponse
model|Modèle de transcription
model_server_default|Celui du serveur
model_default_tag|{0} · par défaut
manage_models|Gérer les modèles
spoken_lang|Langue de l’audio
auto_detect|Automatique
detected|Détectée : {0}
subs_lang|Sous-titres en
original_lang|Sans traduction
lines|Lignes
text_size|Taille du texte
save_srt|Enregistrer les sous-titres (.srt) à l’arrêt
advanced|Avancé
use_vad|Ignorer les silences (détection de voix)
settings|Réglages
first_load_hint|La première fois, le chargement d’un modèle peut prendre jusqu’à une minute.
options_locked|Arrêtez les sous-titres pour changer ces options.
server_setup_title|Connectez votre serveur
server_setup_hint|StreamRemaster transcrit avec un serveur WhisperLive sur votre ordinateur ou votre réseau, ou avec la carte graphique de cet ordinateur.
server_address|Adresse du serveur
server_placeholder|ex. localhost:9090 ou 192.168.1.10:9090
connect|Connecter
server_ok_models|Connecté · {0} modèles
server_ok_one_model|Connecté · 1 modèle
server_plain|Connecté · WhisperLive standard (sans gestion des modèles)
server_checking|Vérification…
server_unreachable|Impossible de joindre le serveur. Est-il allumé ? Vérifiez l’adresse et le pare-feu.
server_timeout|Le serveur n’a pas répondu à temps.
server_bad_url|Cette adresse n’est pas valide.
server_change|Modifier
server_help|Comment installer un serveur ?
server_help_1|Il vous faut un serveur WhisperLive (libre et gratuit) sur un ordinateur, idéalement avec une carte graphique NVIDIA. Les petits modèles fonctionnent aussi avec le seul processeur.
server_help_2|Saisissez ensuite son adresse ici : l’IP de l’ordinateur et le port, ex. 192.168.1.10:9090. S’il tourne sur cet ordinateur, localhost:9090.
server_help_3|Pour télécharger et gérer des modèles depuis cette page, ajoutez au serveur le module de StreamRemaster.
server_help_guide|Guide pas à pas
error_capture|Cet onglet ne peut pas être capturé (pages du navigateur, boutiques d’extensions et PDF sont exclus).
error_no_media|Il n’y a ni vidéo ni audio sur cette page.
error_server_full|Le serveur est occupé. Attente estimée : {0} min.
error_disconnected|Le serveur a fermé la connexion.
error_model_load|⚠ Pas assez de mémoire graphique (VRAM) sur le serveur pour ce modèle. Choisissez un modèle plus petit ou activez « Économiser la mémoire (int8) » dans Avancé.
warn_no_response|⚠ Les sous-titres n’arrivent plus alors qu’il y a du son. Le modèle ne tient sans doute pas dans la mémoire graphique (VRAM) du serveur : choisissez un modèle plus petit ou activez « Économiser la mémoire (int8) » dans Avancé.
warn_slow_load|⚠ Le modèle met trop de temps à charger. Il ne tient peut-être pas dans la mémoire graphique (VRAM) du serveur : choisissez un modèle plus petit ou activez « Économiser la mémoire (int8) » dans Avancé.
error_reload|Rechargez la page (F5) et recommencez.
error_no_server|Configurez d’abord le serveur.
settings_title|StreamRemaster · Réglages
section_subtitles|Sous-titres
section_interface|Interface
section_about|À propos
installed_models|Installés sur le serveur
no_models|Aucun modèle installé pour l’instant.
badge_default|Par défaut
badge_loaded|En mémoire
badge_selected|Choisi
use_model|Utiliser
delete_model|Supprimer
confirm_delete|Supprimer {0} du serveur ? Cela libère {1}.
add_model|Ajouter un modèle
add_model_hint|Collez le nom ou le lien d’un modèle Hugging Face. N’importe quel modèle Whisper convient : ceux de faster-whisper (CTranslate2) s’utilisent tels quels et les normaux (transformers) sont convertis automatiquement. Un lien direct vers un .zip ou .tar.gz contenant un modèle fonctionne aussi.
add_model_placeholder|ex. Systran/faster-whisper-large-v3
download|Télécharger
suggestions|Suggestions :
browse_hf|Voir les modèles Whisper sur Hugging Face
vram_hint|Les grands modèles sont plus précis mais demandent plus de mémoire graphique : small ≈ 1 Go, medium ≈ 2 Go, large ≈ 4 Go.
keep_open|Laissez cette page ouverte jusqu’à la fin du téléchargement.
job_downloading|Téléchargement… {0} sur {1}
job_downloading_nosize|Téléchargement… {0}
job_converting|Conversion au format faster-whisper…
job_extracting|Décompression…
job_ready|Installé
job_error|Échec : {0}
retry|Réessayer
plain_server_hint|C’est un serveur WhisperLive standard : saisissez une taille de modèle (tiny, base, small, medium, large-v3, large-v3-turbo) et le serveur la télécharge la première fois. Pour télécharger n’importe quel modèle d’ici, installez le module de StreamRemaster sur le serveur.
model_name|Nom du modèle
save|Enregistrer
saved|Enregistré
reset_position|Replacer les sous-titres
position_reset_done|C’est fait : ils reviendront en bas.
section_performance|Performances
performance_hint|Si la carte graphique du serveur manque de mémoire (sous-titres qui n’arrivent pas ou alerte mémoire), ces deux options en libèrent beaucoup. Elles ne marchent qu’avec le serveur de StreamRemaster.
precision|Précision du modèle
precision_auto|Automatique
precision_int8|Économiser la mémoire (int8)
precision_hint|int8 utilise environ la moitié de la mémoire graphique et, en pratique, écrit le même texte.
translator_device|Le traducteur tourne sur
device_gpu|La carte graphique
device_cpu|Le processeur (CPU)
translator_device_hint|Sur le processeur, il libère de la mémoire graphique, mais les sous-titres traduits arrivent un peu plus tard.
interface_lang|Langue de l’interface
lang_auto|Celle du navigateur
about_text|Code source disponible (licence PolyForm Noncommercial). L’audio ne va qu’au serveur que vous configurez ici ; rien n’est envoyé ailleurs.
about_based|Basé sur WhisperLive, de Collabora.
source_code|Code source
subtitle_preview|Voici à quoi ressembleront vos sous-titres.
err_invalid_source|Ce n’est ni un nom de modèle Hugging Face ni un lien.
err_unsupported_url|Uniquement des liens Hugging Face ou des liens directs vers des fichiers .zip / .tar.gz.
err_repo_not_found|Ce modèle n’existe pas sur Hugging Face (vérifiez le nom).
err_gated_repo|Ce modèle demande d’accepter ses conditions sur Hugging Face ; le serveur a besoin d’un HF_TOKEN.
err_not_whisper|Ce n’est pas un modèle Whisper.
err_no_weights|Ce dépôt ne contient pas les poids du modèle.
err_network_error|Erreur réseau. Réessayez : cela reprend là où ça s’est arrêté.
err_download_failed|Le téléchargement a échoué.
err_convert_failed|Impossible de convertir le modèle.
err_bad_archive|L’archive est endommagée ou dangereuse.
err_already_downloading|Il est déjà en cours de téléchargement.
err_already_installed|Il est déjà installé.
err_management_disabled|La gestion des modèles est désactivée sur ce serveur.
err_is_default|C’est le modèle par défaut du serveur ; il ne peut pas être supprimé d’ici.
err_in_use|Une transcription en cours l’utilise.
err_not_found|Ce modèle n’est plus sur le serveur.
err_server_error|Erreur du serveur.
err_unreachable|Impossible de joindre le serveur.
err_timeout|Le serveur n’a pas répondu à temps.
err_unknown|Erreur inattendue ({0}).
updates|Mises à jour
check_updates|Rechercher des mises à jour
check_again|Rechercher à nouveau
update_now|Mettre à jour
update_available|La version {0} est disponible (vous avez la {1}).
update_latest|Vous avez la dernière version ({0}).
update_rate_limited|GitHub limite les vérifications pendant un moment. Réessayez plus tard.
update_failed|Impossible de rechercher des mises à jour. Vérifiez la connexion et réessayez.
update_how_firefox|Firefox installe les nouvelles versions tout seul. Pour l’avoir tout de suite, ouvrez about:addons, cliquez sur la roue dentée et choisissez « Rechercher des mises à jour ». Une version qui vient de sortir peut mettre quelques jours à arriver sur le site des modules complémentaires.
update_how_chromium|Pour mettre à jour, téléchargez le zip Chromium sur la page de la version, décompressez-le par-dessus l’ancien dossier et cliquez sur l’icône de rechargement de la carte StreamRemaster dans chrome://extensions. Vos réglages sont conservés.
update_privacy|La recherche demande seulement à GitHub le numéro de la dernière version ; rien d’autre n’est envoyé.
server_update_available|Votre serveur a la version {0} et la {1} est disponible. Pour le mettre à jour, lancez ceci sur l’ordinateur qui l’héberge :
server_version_unknown|Votre serveur n’indique pas sa version : il est donc antérieur à cette vérification. Pour le mettre à jour, lancez ceci sur l’ordinateur qui l’héberge :
server_update_latest|Votre serveur est à jour ({0}).
server_update_note|Les modèles restent dans le volume Docker et ne sont pas retéléchargés. Si vous avez modifié docker-compose.yml et que git pull proteste, lancez git stash avant et git stash pop après.
setup_or|ou
use_local|Utiliser cet ordinateur
use_local_hint|Whisper tourne sur la carte graphique de cet ordinateur, sans serveur. Le modèle se télécharge une fois, dans les Paramètres.
local_footer|Cet ordinateur
local_none|Aucun modèle : téléchargez-en un
local_intro|Whisper tourne dans le navigateur, sur votre carte graphique (WebGPU). Chaque modèle se télécharge une fois depuis Hugging Face et reste dans le navigateur. Les plus gros écrivent mieux et demandent plus de mémoire graphique.
local_sizes|Téléchargement {0} · occupe {1} · environ {2} de mémoire graphique
local_progress|Téléchargement… {0} sur {1}
local_cancel|Annuler
local_gpu|Carte graphique : {0}
badge_downloaded|Téléchargé
error_no_webgpu|Ce navigateur ne peut pas utiliser la carte graphique (WebGPU) : il ne peut pas transcrire sur cet ordinateur.
error_local_missing|Téléchargez d’abord un modèle, dans Paramètres → Modèles sur cet ordinateur.
error_local_failed|La transcription sur cet ordinateur s’est arrêtée à cause d’une erreur.
error_local_vram|⚠ Pas assez de mémoire graphique sur cet ordinateur pour ce modèle. Choisissez-en un plus petit.
local_download_failed|Le téléchargement a échoué ({0}).
local_confirm_delete|Supprimer le modèle {0} de cet ordinateur ? Cela libère {1}.
local_only_english|Sur cet ordinateur, les sous-titres ne peuvent être traduits qu’en anglais.
"""

LANGS['de'] = """
error_local_lost|Die Grafikkarte hat das Transkriptionsmodell mehrmals hintereinander gestoppt.
fg_hq_badge|Für leistungsstarke Grafikkarten
where_fg_models|Wo die Modelle liegen
fg_local_title|Modelle für flüssiges Video auf diesem Computer
fg_server_title|Modelle für flüssiges Video auf dem Server
fg_server_intro|Der Server bewahrt sie nur auf: Das gewählte Modell wird von ihm geladen und läuft auf der Grafikkarte dieses Computers.
fg_server_none|Der Server hat noch keine Modelle für flüssiges Video.
fg_server_old|Dieser Server bewahrt keine Modelle für flüssiges Video auf: Aktualisiere ihn auf die neueste Version.
fg_add_server_title|Zum Server hinzufügen
fg_server_loading|Modell wird vom Server geladen…
section_transcription|Transkriptionsmodelle
transcription_intro|Wähle, wo die Sprache zu Text wird: auf einem WhisperLive-Server oder auf der Grafikkarte dieses Computers.
where_transcribe|Wo transkribieren
engine_server|Auf dem Server
engine_local|Auf diesem Computer
trans_server_title|Transkriptionsmodelle auf dem Server
trans_local_title|Transkriptionsmodelle auf diesem Computer
badge_in_use|Aktiv
fg_downloaded_title|Heruntergeladen
fg_add_title|Modell hinzufügen
fg_add_url_placeholder|Adresse einer Modelldatei (.stmodel)
fg_download_failed|Der Download ist fehlgeschlagen ({0}). Lade die Datei mit dem Browser herunter und wähle sie auf diesem Computer aus.
fg_memory|Grafikspeicher: etwa {0} bei einem 1080p-Video
fg_memory_4k|etwa {0} beim Hochskalieren von 1080p auf 4K
fg_memory_now|Belegter Grafikspeicher: etwa {0}
fg_file_size|Datei: {0}
fg_options|Optionen
fg_sharpen|Schärfe
fg_sharpen_off|Aus
fg_sharpen_soft|Leicht
fg_sharpen_medium|Mittel
fg_sharpen_strong|Stark
fg_resolution|Zielauflösung der Hochskalierung
fg_res_original|Original (ohne Hochskalierung)
fg_model|Modell für flüssiges Video
fg_kind_sr|Nur Hochskalierung
fg_kind_fi|Nur Zwischenbilder
fg_builtin|Integriert
fg_model_none|Keines (ohne KI)
section_fgmodels|Modelle für flüssiges Video
fg_models_hint|Flüssiges Video läuft immer auf der Grafikkarte dieses Computers. StreamRemaster ist in der Erweiterung enthalten; weitere Modelle können auf diesem Computer oder auf deinem Server liegen.
fg_add_model|Datei auf diesem Computer wählen
fg_no_models|Noch keine heruntergeladenen Modelle.
fg_model_bad|Diese Datei ist kein gültiges Modell.
tab_subs|Untertitel
tab_fg|Flüssiges Video
fg_start|Flüssiges Video einschalten
fg_stop|Flüssiges Video ausschalten
fg_target|Ziel-FPS
fg_target_display|Wie der Bildschirm
fg_state_off|Aus
fg_state_measuring|Video wird gemessen…
fg_state_on|{0} fps (Video mit {1} fps)
fg_no_video|Auf dieser Seite wird kein Video abgespielt.
fg_no_webgpu|Dieser Browser kann die GPU dafür nicht nutzen (WebGPU ist nicht verfügbar).
fg_cannot_read|Dieses Video kann nicht gelesen werden: Es ist geschützt oder stammt von einer anderen Website.
fg_unavailable|Diese Seite lässt keine Erweiterungen zu.
fg_auto_start|Flüssiges Video beim Abspielen eines Videos einschalten
subs_auto_start|Untertitel beim Abspielen eines Videos starten
auto_start_hint|In diesem Browser funktioniert das nur in Tabs, in denen du auf die Schaltfläche der Erweiterung geklickt hast, bis sie zu einer anderen Website wechseln.
fg_allow_all_sites|Auf allen Websites erlauben
extName|StreamRemaster
extDescription|Live-Untertitel für jeden Tab, transkribiert und übersetzt von deinem eigenen Whisper-Server.
start|Untertitel starten
stop|Untertitel beenden
status_idle|Bereit
status_connecting|Verbinde…
status_loading|Lade das Modell…
status_listening|Höre zu…
status_live|Live
status_stalled|Audio angehalten
status_error|Fehler
status_noresponse|Keine Antwort
model|Transkriptionsmodell
model_server_default|Das des Servers
model_default_tag|{0} · Standard
manage_models|Modelle verwalten
spoken_lang|Sprache des Audios
auto_detect|Automatisch
detected|Erkannt: {0}
subs_lang|Untertitel auf
original_lang|Ohne Übersetzung
lines|Zeilen
text_size|Textgröße
save_srt|Untertitel (.srt) beim Beenden speichern
advanced|Erweitert
use_vad|Stille überspringen (Spracherkennung)
settings|Einstellungen
first_load_hint|Beim ersten Mal kann das Laden eines Modells bis zu einer Minute dauern.
options_locked|Beende die Untertitel, um diese Optionen zu ändern.
server_setup_title|Verbinde deinen Server
server_setup_hint|StreamRemaster transkribiert mit einem WhisperLive-Server auf deinem Computer oder in deinem Netzwerk oder mit der Grafikkarte dieses Computers.
server_address|Serveradresse
server_placeholder|z. B. localhost:9090 oder 192.168.1.10:9090
connect|Verbinden
server_ok_models|Verbunden · {0} Modelle
server_ok_one_model|Verbunden · 1 Modell
server_plain|Verbunden · Standard-WhisperLive (ohne Modellverwaltung)
server_checking|Prüfe…
server_unreachable|Der Server ist nicht erreichbar. Läuft er? Prüfe die Adresse und die Firewall.
server_timeout|Der Server hat nicht rechtzeitig geantwortet.
server_bad_url|Diese Adresse ist ungültig.
server_change|Ändern
server_help|Wie richte ich einen Server ein?
server_help_1|Du brauchst einen WhisperLive-Server (frei und kostenlos) auf einem Computer, am besten mit einer NVIDIA-Grafikkarte. Kleine Modelle laufen auch nur auf dem Prozessor.
server_help_2|Gib dann hier seine Adresse ein: die IP des Computers und den Port, z. B. 192.168.1.10:9090. Läuft er auf diesem Computer, localhost:9090.
server_help_3|Um Modelle von dieser Seite aus herunterzuladen und zu verwalten, füge dem Server das Stream-Transcription-Add-on hinzu.
server_help_guide|Schritt-für-Schritt-Anleitung
error_capture|Dieser Tab lässt sich nicht aufnehmen (Browserseiten, Erweiterungsshops und PDFs sind gesperrt).
error_no_media|Auf dieser Seite gibt es weder Video noch Audio.
error_server_full|Der Server ist ausgelastet. Geschätzte Wartezeit: {0} min.
error_disconnected|Der Server hat die Verbindung geschlossen.
error_model_load|⚠ Auf dem Server reicht der Grafikspeicher (VRAM) für dieses Modell nicht. Wähle ein kleineres Modell oder schalte unter Erweitert „Speicher sparen (int8)“ ein.
warn_no_response|⚠ Es kommen keine Untertitel mehr, obwohl Ton da ist. Wahrscheinlich passt das Modell nicht in den Grafikspeicher (VRAM) des Servers: Wähle ein kleineres Modell oder schalte unter Erweitert „Speicher sparen (int8)“ ein.
warn_slow_load|⚠ Das Modell lädt zu lange. Vielleicht passt es nicht in den Grafikspeicher (VRAM) des Servers: Wähle ein kleineres Modell oder schalte unter Erweitert „Speicher sparen (int8)“ ein.
error_reload|Lade die Seite neu (F5) und starte erneut.
error_no_server|Richte zuerst den Server ein.
settings_title|StreamRemaster · Einstellungen
section_subtitles|Untertitel
section_interface|Oberfläche
section_about|Über
installed_models|Auf dem Server installiert
no_models|Noch keine Modelle installiert.
badge_default|Standard
badge_loaded|Im Speicher
badge_selected|Ausgewählt
use_model|Verwenden
delete_model|Löschen
confirm_delete|{0} vom Server löschen? Das gibt {1} frei.
add_model|Ein Modell hinzufügen
add_model_hint|Füge den Namen oder den Link eines Modells von Hugging Face ein. Jedes Whisper-Modell geht: faster-whisper-Modelle (CTranslate2) werden direkt genutzt, normale (transformers) werden automatisch umgewandelt. Ein direkter Link auf ein .zip oder .tar.gz mit einem Modell geht auch.
add_model_placeholder|z. B. Systran/faster-whisper-large-v3
download|Herunterladen
suggestions|Vorschläge:
browse_hf|Whisper-Modelle auf Hugging Face ansehen
vram_hint|Größere Modelle sind genauer, brauchen aber mehr Grafikspeicher: small ≈ 1 GB, medium ≈ 2 GB, large ≈ 4 GB.
keep_open|Lass diese Seite offen, bis der Download fertig ist.
job_downloading|Lade herunter… {0} von {1}
job_downloading_nosize|Lade herunter… {0}
job_converting|Wandle ins faster-whisper-Format um…
job_extracting|Entpacke…
job_ready|Installiert
job_error|Fehlgeschlagen: {0}
retry|Erneut versuchen
plain_server_hint|Das ist ein Standard-WhisperLive-Server: Gib eine Modellgröße ein (tiny, base, small, medium, large-v3, large-v3-turbo), der Server lädt sie beim ersten Mal herunter. Um beliebige Modelle von hier herunterzuladen, installiere das Stream-Transcription-Add-on auf dem Server.
model_name|Modellname
save|Speichern
saved|Gespeichert
reset_position|Untertitelposition zurücksetzen
position_reset_done|Erledigt: Sie wandern wieder nach unten.
section_performance|Leistung
performance_hint|Wenn der Grafikkarte des Servers der Speicher ausgeht (Untertitel kommen nicht an oder eine Speicherwarnung erscheint), geben diese beiden Optionen viel frei. Sie funktionieren nur mit dem Stream-Transcription-Server.
precision|Modellgenauigkeit
precision_auto|Automatisch
precision_int8|Speicher sparen (int8)
precision_hint|int8 braucht etwa halb so viel Grafikspeicher und schreibt in der Praxis denselben Text.
translator_device|Der Übersetzer läuft auf
device_gpu|Grafikkarte
device_cpu|Prozessor (CPU)
translator_device_hint|Auf dem Prozessor wird Grafikspeicher frei, aber übersetzte Untertitel kommen etwas später.
interface_lang|Sprache der Oberfläche
lang_auto|Wie der Browser
about_text|Quellcode verfügbar (PolyForm-Noncommercial-Lizenz). Das Audio geht nur an den Server, den du hier einrichtest; nichts wird woandershin geschickt.
about_based|Basiert auf WhisperLive von Collabora.
source_code|Quellcode
subtitle_preview|So sehen deine Untertitel aus.
err_invalid_source|Das ist weder ein Hugging-Face-Modellname noch ein Link.
err_unsupported_url|Nur Hugging-Face-Links oder direkte Links auf .zip-/.tar.gz-Dateien.
err_repo_not_found|Dieses Modell gibt es auf Hugging Face nicht (prüfe den Namen).
err_gated_repo|Für dieses Modell müssen auf Hugging Face Bedingungen akzeptiert werden; der Server braucht ein HF_TOKEN.
err_not_whisper|Das ist kein Whisper-Modell.
err_no_weights|Dieses Repository enthält keine Modellgewichte.
err_network_error|Netzwerkfehler. Versuch es noch mal: Es geht dort weiter, wo es aufgehört hat.
err_download_failed|Der Download ist fehlgeschlagen.
err_convert_failed|Das Modell konnte nicht umgewandelt werden.
err_bad_archive|Das Archiv ist beschädigt oder unsicher.
err_already_downloading|Es wird schon heruntergeladen.
err_already_installed|Es ist schon installiert.
err_management_disabled|Die Modellverwaltung ist auf diesem Server ausgeschaltet.
err_is_default|Das ist das Standardmodell des Servers; es kann hier nicht gelöscht werden.
err_in_use|Eine laufende Transkription verwendet es.
err_not_found|Dieses Modell ist nicht mehr auf dem Server.
err_server_error|Serverfehler.
err_unreachable|Der Server ist nicht erreichbar.
err_timeout|Der Server hat nicht rechtzeitig geantwortet.
err_unknown|Unerwarteter Fehler ({0}).
updates|Updates
check_updates|Nach Updates suchen
check_again|Erneut suchen
update_now|Aktualisieren
update_available|Version {0} ist verfügbar (Sie haben {1}).
update_latest|Sie haben die neueste Version ({0}).
update_rate_limited|GitHub begrenzt die Abfragen für eine Weile. Versuchen Sie es später erneut.
update_failed|Die Suche nach Updates ist fehlgeschlagen. Prüfen Sie die Verbindung und versuchen Sie es erneut.
update_how_firefox|Firefox installiert neue Versionen von selbst. Um sie sofort zu bekommen, öffnen Sie about:addons, klicken Sie auf das Zahnrad und wählen Sie „Auf Updates überprüfen“. Eine gerade erschienene Version kann einige Tage brauchen, bis sie auf der Add-on-Website ist.
update_how_chromium|Zum Aktualisieren laden Sie das Chromium-ZIP von der Seite der Version herunter, entpacken es über den alten Ordner und klicken in chrome://extensions auf der Karte von StreamRemaster auf das Neu-laden-Symbol. Ihre Einstellungen bleiben erhalten.
update_privacy|Bei der Suche wird GitHub nur nach der Nummer der neuesten Version gefragt; sonst wird nichts gesendet.
server_update_available|Ihr Server hat Version {0}, und {1} ist verfügbar. Führen Sie zum Aktualisieren dies auf dem Computer aus, auf dem er läuft:
server_version_unknown|Ihr Server meldet seine Version nicht, er ist also älter als diese Prüfung. Führen Sie zum Aktualisieren dies auf dem Computer aus, auf dem er läuft:
server_update_latest|Ihr Server ist aktuell ({0}).
server_update_note|Die Modelle bleiben im Docker-Volume und werden nicht erneut heruntergeladen. Wenn Sie docker-compose.yml geändert haben und git pull sich beschwert, führen Sie vorher git stash und danach git stash pop aus.
setup_or|oder
use_local|Diesen Computer verwenden
use_local_hint|Whisper läuft auf der Grafikkarte dieses Computers, ohne Server. Das Modell wird einmal in den Einstellungen heruntergeladen.
local_footer|Dieser Computer
local_none|Noch kein Modell: lade eines herunter
local_intro|Whisper läuft im Browser auf deiner Grafikkarte (WebGPU). Jedes Modell wird einmal von Hugging Face geladen und bleibt im Browser. Die größeren schreiben besser und brauchen mehr Grafikspeicher.
local_sizes|Download {0} · belegt {1} · etwa {2} Grafikspeicher
local_progress|Wird heruntergeladen… {0} von {1}
local_cancel|Abbrechen
local_gpu|Grafikkarte: {0}
badge_downloaded|Heruntergeladen
error_no_webgpu|Dieser Browser kann die Grafikkarte (WebGPU) nicht nutzen und daher nicht auf diesem Computer transkribieren.
error_local_missing|Lade zuerst ein Modell herunter, unter Einstellungen → Modelle auf diesem Computer.
error_local_failed|Die Transkription auf diesem Computer wurde wegen eines Fehlers beendet.
error_local_vram|⚠ Nicht genug Grafikspeicher auf diesem Computer für dieses Modell. Wähle ein kleineres.
local_download_failed|Der Download ist fehlgeschlagen ({0}).
local_confirm_delete|Modell {0} von diesem Computer löschen? Das gibt {1} frei.
local_only_english|Auf diesem Computer lassen sich die Untertitel nur ins Englische übersetzen.
"""

LANGS['it'] = """
error_local_lost|La scheda video ha fermato il modello di trascrizione più volte di seguito.
fg_hq_badge|Per schede video potenti
where_fg_models|Dove sono i modelli
fg_local_title|Modelli per video fluido su questo computer
fg_server_title|Modelli per video fluido sul server
fg_server_intro|Il server si limita a conservarli: il modello scelto viene scaricato da lì e funziona sulla scheda video di questo computer.
fg_server_none|Il server non ha ancora modelli per video fluido.
fg_server_old|Questo server non conserva modelli per video fluido: aggiornalo all’ultima versione.
fg_add_server_title|Aggiungi al server
fg_server_loading|Download del modello dal server…
section_transcription|Modelli di trascrizione
transcription_intro|Scegli dove la voce diventa testo: su un server WhisperLive o sulla scheda video di questo computer.
where_transcribe|Dove trascrivere
engine_server|Sul server
engine_local|Su questo computer
trans_server_title|Modelli di trascrizione sul server
trans_local_title|Modelli di trascrizione su questo computer
badge_in_use|In uso
fg_downloaded_title|Scaricati
fg_add_title|Aggiungi un modello
fg_add_url_placeholder|Indirizzo di un file di modello (.stmodel)
fg_download_failed|Impossibile scaricarlo ({0}). Scarica il file con il browser e sceglilo da questo computer.
fg_memory|Memoria video: circa {0} con un video 1080p
fg_memory_4k|circa {0} ingrandendo da 1080p a 4K
fg_memory_now|Memoria video in uso: circa {0}
fg_file_size|File: {0}
fg_options|Opzioni
fg_sharpen|Nitidezza
fg_sharpen_off|Disattivata
fg_sharpen_soft|Leggera
fg_sharpen_medium|Media
fg_sharpen_strong|Forte
fg_resolution|Risoluzione di destinazione dell'ingrandimento
fg_res_original|Originale (senza ingrandimento)
fg_model|Modello per video fluido
fg_kind_sr|Solo ingrandimento
fg_kind_fi|Solo fotogrammi intermedi
fg_builtin|Integrato
fg_model_none|Nessuno (senza IA)
section_fgmodels|Modelli per video fluido
fg_models_hint|Il video fluido funziona sempre sulla scheda video di questo computer. StreamRemaster è incluso nell’estensione; altri modelli possono stare su questo computer o sul tuo server.
fg_add_model|Scegli un file su questo computer
fg_no_models|Nessun modello scaricato per ora.
fg_model_bad|Questo file non è un modello valido.
tab_subs|Sottotitoli
tab_fg|Video fluido
fg_start|Attiva video fluido
fg_stop|Disattiva video fluido
fg_target|FPS desiderati
fg_target_display|Come lo schermo
fg_state_off|Disattivato
fg_state_measuring|Misurazione del video…
fg_state_on|{0} fps (video a {1} fps)
fg_no_video|In questa pagina non è in riproduzione alcun video.
fg_no_webgpu|Questo browser non può usare la GPU per questo (WebGPU non è disponibile).
fg_cannot_read|Questo video non può essere letto: è protetto o proviene da un altro sito.
fg_unavailable|Questa pagina non consente le estensioni.
fg_auto_start|Attiva il video fluido quando parte un video
subs_auto_start|Avvia i sottotitoli quando parte un video
auto_start_hint|In questo browser funziona solo nelle schede in cui hai fatto clic sul pulsante dell'estensione, finché non passano a un altro sito.
fg_allow_all_sites|Consenti su tutti i siti
extName|StreamRemaster
extDescription|Sottotitoli in diretta per qualsiasi scheda, trascritti e tradotti dal tuo server Whisper.
start|Attiva sottotitoli
stop|Disattiva sottotitoli
status_idle|Pronto
status_connecting|Connessione…
status_loading|Caricamento del modello…
status_listening|In ascolto…
status_live|In diretta
status_stalled|Audio fermo
status_error|Errore
status_noresponse|Nessuna risposta
model|Modello di trascrizione
model_server_default|Quello del server
model_default_tag|{0} · predefinito
manage_models|Gestisci modelli
spoken_lang|Lingua dell’audio
auto_detect|Automatico
detected|Rilevata: {0}
subs_lang|Sottotitoli in
original_lang|Senza traduzione
lines|Righe
text_size|Dimensione del testo
save_srt|Salva i sottotitoli (.srt) quando ti fermi
advanced|Avanzate
use_vad|Salta i silenzi (rilevamento della voce)
settings|Impostazioni
first_load_hint|La prima volta il caricamento di un modello può richiedere fino a un minuto.
options_locked|Disattiva i sottotitoli per cambiare queste opzioni.
server_setup_title|Collega il tuo server
server_setup_hint|StreamRemaster trascrive con un server WhisperLive sul tuo computer o nella tua rete, oppure con la scheda video di questo computer.
server_address|Indirizzo del server
server_placeholder|es. localhost:9090 o 192.168.1.10:9090
connect|Collega
server_ok_models|Collegato · {0} modelli
server_ok_one_model|Collegato · 1 modello
server_plain|Collegato · WhisperLive standard (senza gestione dei modelli)
server_checking|Verifica…
server_unreachable|Impossibile raggiungere il server. È acceso? Controlla l’indirizzo e il firewall.
server_timeout|Il server non ha risposto in tempo.
server_bad_url|Questo indirizzo non è valido.
server_change|Cambia
server_help|Come configuro un server?
server_help_1|Ti serve un server WhisperLive (libero e gratuito) su un computer, meglio se con una scheda grafica NVIDIA. I modelli piccoli funzionano anche solo con il processore.
server_help_2|Poi scrivi qui il suo indirizzo: l’IP del computer e la porta, es. 192.168.1.10:9090. Se è su questo stesso computer, localhost:9090.
server_help_3|Per scaricare e gestire i modelli da questa pagina, aggiungi al server il componente di StreamRemaster.
server_help_guide|Guida passo passo
error_capture|Questa scheda non si può catturare (pagine del browser, negozi di estensioni e PDF sono esclusi).
error_no_media|In questa pagina non ci sono video né audio.
error_server_full|Il server è occupato. Attesa stimata: {0} min.
error_disconnected|Il server ha chiuso la connessione.
error_model_load|⚠ Il server non ha abbastanza memoria grafica (VRAM) per questo modello. Scegli un modello più piccolo o attiva “Risparmia memoria (int8)” in Avanzate.
warn_no_response|⚠ I sottotitoli non arrivano più anche se c’è audio. Probabilmente il modello non entra nella memoria grafica (VRAM) del server: scegli un modello più piccolo o attiva “Risparmia memoria (int8)” in Avanzate.
warn_slow_load|⚠ Il modello ci mette troppo a caricarsi. Forse non entra nella memoria grafica (VRAM) del server: scegli un modello più piccolo o attiva “Risparmia memoria (int8)” in Avanzate.
error_reload|Ricarica la pagina (F5) e ricomincia.
error_no_server|Prima configura il server.
settings_title|StreamRemaster · Impostazioni
section_subtitles|Sottotitoli
section_interface|Interfaccia
section_about|Informazioni
installed_models|Installati sul server
no_models|Ancora nessun modello installato.
badge_default|Predefinito
badge_loaded|In memoria
badge_selected|Scelto
use_model|Usa
delete_model|Elimina
confirm_delete|Eliminare {0} dal server? Libera {1}.
add_model|Aggiungi un modello
add_model_hint|Incolla il nome o il link di un modello di Hugging Face. Va bene qualsiasi modello Whisper: quelli di faster-whisper (CTranslate2) si usano così come sono e quelli normali (transformers) vengono convertiti da soli. Va bene anche un link diretto a un .zip o .tar.gz con un modello.
add_model_placeholder|es. Systran/faster-whisper-large-v3
download|Scarica
suggestions|Suggerimenti:
browse_hf|Vedi i modelli Whisper su Hugging Face
vram_hint|I modelli grandi sono più precisi ma chiedono più memoria della scheda grafica: small ≈ 1 GB, medium ≈ 2 GB, large ≈ 4 GB.
keep_open|Lascia aperta questa pagina finché il download non finisce.
job_downloading|Scaricamento… {0} di {1}
job_downloading_nosize|Scaricamento… {0}
job_converting|Conversione nel formato faster-whisper…
job_extracting|Estrazione…
job_ready|Installato
job_error|Non riuscito: {0}
retry|Riprova
plain_server_hint|È un server WhisperLive standard: scrivi una dimensione di modello (tiny, base, small, medium, large-v3, large-v3-turbo) e il server la scarica la prima volta. Per scaricare qualsiasi modello da qui, installa sul server il componente di StreamRemaster.
model_name|Nome del modello
save|Salva
saved|Salvato
reset_position|Riposiziona i sottotitoli
position_reset_done|Fatto: torneranno in basso.
section_performance|Prestazioni
performance_hint|Se la scheda grafica del server resta senza memoria (sottotitoli che non arrivano o un avviso di memoria), queste due opzioni ne liberano parecchia. Funzionano solo con il server di StreamRemaster.
precision|Precisione del modello
precision_auto|Automatica
precision_int8|Risparmia memoria (int8)
precision_hint|int8 usa circa metà della memoria grafica e, in pratica, scrive lo stesso testo.
translator_device|Il traduttore gira su
device_gpu|Scheda grafica
device_cpu|Processore (CPU)
translator_device_hint|Sul processore libera memoria grafica, ma i sottotitoli tradotti arrivano un po’ dopo.
interface_lang|Lingua dell’interfaccia
lang_auto|Quella del browser
about_text|Codice sorgente disponibile (licenza PolyForm Noncommercial). L’audio va solo al server che configuri qui; non viene inviato altrove.
about_based|Basato su WhisperLive di Collabora.
source_code|Codice sorgente
subtitle_preview|Ecco come appariranno i tuoi sottotitoli.
err_invalid_source|Non è un nome di modello di Hugging Face né un link.
err_unsupported_url|Solo link di Hugging Face o link diretti a file .zip / .tar.gz.
err_repo_not_found|Quel modello non esiste su Hugging Face (controlla il nome).
err_gated_repo|Quel modello chiede di accettare le sue condizioni su Hugging Face; il server ha bisogno di un HF_TOKEN.
err_not_whisper|Non è un modello Whisper.
err_no_weights|Quel repository non ha i pesi del modello.
err_network_error|Errore di rete. Riprova: riparte da dove si era fermato.
err_download_failed|Il download non è riuscito.
err_convert_failed|Non è stato possibile convertire il modello.
err_bad_archive|L’archivio è danneggiato o non è sicuro.
err_already_downloading|Lo sta già scaricando.
err_already_installed|È già installato.
err_management_disabled|La gestione dei modelli è disattivata su questo server.
err_is_default|È il modello predefinito del server; non si può eliminare da qui.
err_in_use|Lo sta usando una trascrizione in corso.
err_not_found|Quel modello non è più sul server.
err_server_error|Errore del server.
err_unreachable|Impossibile raggiungere il server.
err_timeout|Il server non ha risposto in tempo.
err_unknown|Errore imprevisto ({0}).
updates|Aggiornamenti
check_updates|Cerca aggiornamenti
check_again|Cerca di nuovo
update_now|Aggiorna
update_available|È disponibile la versione {0} (hai la {1}).
update_latest|Hai l’ultima versione ({0}).
update_rate_limited|GitHub sta limitando le verifiche per un po’. Riprova più tardi.
update_failed|Impossibile cercare aggiornamenti. Controlla la connessione e riprova.
update_how_firefox|Firefox installa da solo le nuove versioni. Per averla subito, apri about:addons, fai clic sull’icona dell’ingranaggio e scegli “Controlla aggiornamenti”. Una versione appena uscita può impiegare qualche giorno ad arrivare al sito dei componenti aggiuntivi.
update_how_chromium|Per aggiornare, scarica lo zip per Chromium dalla pagina della versione, estrailo sopra la vecchia cartella e fai clic sull’icona di ricarica nella scheda di StreamRemaster in chrome://extensions. Le impostazioni restano.
update_privacy|La ricerca chiede a GitHub solo il numero dell’ultima versione; non viene inviato nient’altro.
server_update_available|Il tuo server ha la versione {0} ed è disponibile la {1}. Per aggiornarlo, esegui questo sul computer che lo ospita:
server_version_unknown|Il tuo server non dice quale versione ha, quindi è precedente a questa verifica. Per aggiornarlo, esegui questo sul computer che lo ospita:
server_update_latest|Il tuo server è aggiornato ({0}).
server_update_note|I modelli restano nel volume Docker e non vengono riscaricati. Se hai modificato docker-compose.yml e git pull si lamenta, esegui git stash prima e git stash pop dopo.
setup_or|oppure
use_local|Usa questo computer
use_local_hint|Whisper gira sulla scheda video di questo computer, senza server. Il modello si scarica una volta, nelle Impostazioni.
local_footer|Questo computer
local_none|Nessun modello: scaricane uno
local_intro|Whisper gira nel browser, sulla tua scheda video (WebGPU). Ogni modello si scarica una volta da Hugging Face e resta nel browser. I più grandi scrivono meglio e richiedono più memoria video.
local_sizes|Download {0} · occupa {1} · circa {2} di memoria video
local_progress|Download in corso… {0} di {1}
local_cancel|Annulla
local_gpu|Scheda video: {0}
badge_downloaded|Scaricato
error_no_webgpu|Questo browser non può usare la scheda video (WebGPU), quindi non può trascrivere su questo computer.
error_local_missing|Prima scarica un modello, in Impostazioni → Modelli su questo computer.
error_local_failed|La trascrizione su questo computer si è fermata per un errore.
error_local_vram|⚠ Memoria video insufficiente su questo computer per questo modello. Scegline uno più piccolo.
local_download_failed|Il download non è riuscito ({0}).
local_confirm_delete|Eliminare il modello {0} da questo computer? Libera {1}.
local_only_english|Su questo computer i sottotitoli si possono tradurre solo in inglese.
"""

LANGS['nl'] = """
error_local_lost|De videokaart heeft het transcriptiemodel meerdere keren achter elkaar gestopt.
fg_hq_badge|Voor krachtige videokaarten
where_fg_models|Waar de modellen staan
fg_local_title|Modellen voor vloeiende video op deze computer
fg_server_title|Modellen voor vloeiende video op de server
fg_server_intro|De server bewaart ze alleen: het gekozen model wordt ervan gedownload en draait op de videokaart van deze computer.
fg_server_none|De server heeft nog geen modellen voor vloeiende video.
fg_server_old|Deze server bewaart geen modellen voor vloeiende video: werk hem bij naar de nieuwste versie.
fg_add_server_title|Toevoegen aan de server
fg_server_loading|Model wordt van de server gedownload…
section_transcription|Transcriptiemodellen
transcription_intro|Kies waar spraak tekst wordt: op een WhisperLive-server of op de videokaart van deze computer.
where_transcribe|Waar transcriberen
engine_server|Op de server
engine_local|Op deze computer
trans_server_title|Transcriptiemodellen op de server
trans_local_title|Transcriptiemodellen op deze computer
badge_in_use|In gebruik
fg_downloaded_title|Gedownload
fg_add_title|Model toevoegen
fg_add_url_placeholder|Adres van een modelbestand (.stmodel)
fg_download_failed|Downloaden is mislukt ({0}). Download het bestand met de browser en kies het op deze computer.
fg_memory|Videogeheugen: ongeveer {0} bij een 1080p-video
fg_memory_4k|ongeveer {0} bij opschalen van 1080p naar 4K
fg_memory_now|Videogeheugen in gebruik: ongeveer {0}
fg_file_size|Bestand: {0}
fg_options|Opties
fg_sharpen|Scherpte
fg_sharpen_off|Uit
fg_sharpen_soft|Licht
fg_sharpen_medium|Gemiddeld
fg_sharpen_strong|Sterk
fg_resolution|Doelresolutie van de opschaling
fg_res_original|Origineel (zonder opschaling)
fg_model|Model voor vloeiende video
fg_kind_sr|Alleen opschaling
fg_kind_fi|Alleen tussenbeelden
fg_builtin|Ingebouwd
fg_model_none|Geen (zonder AI)
section_fgmodels|Modellen voor vloeiende video
fg_models_hint|Vloeiende video draait altijd op de videokaart van deze computer. StreamRemaster zit bij de extensie; andere modellen kunnen op deze computer of op je server staan.
fg_add_model|Kies een bestand op deze computer
fg_no_models|Nog geen gedownloade modellen.
fg_model_bad|Dit bestand is geen geldig model.
tab_subs|Ondertiteling
tab_fg|Vloeiende video
fg_start|Vloeiende video inschakelen
fg_stop|Vloeiende video uitschakelen
fg_target|Doel-FPS
fg_target_display|Gelijk aan het scherm
fg_state_off|Uit
fg_state_measuring|Video wordt gemeten…
fg_state_on|{0} fps (video op {1} fps)
fg_no_video|Er wordt geen video afgespeeld op deze pagina.
fg_no_webgpu|Deze browser kan de GPU hiervoor niet gebruiken (WebGPU is niet beschikbaar).
fg_cannot_read|Deze video kan niet worden gelezen: hij is beveiligd of komt van een andere site.
fg_unavailable|Deze pagina staat geen extensies toe.
fg_auto_start|Vloeiende video inschakelen zodra een video speelt
subs_auto_start|Ondertiteling starten zodra een video speelt
auto_start_hint|In deze browser werkt het alleen in tabbladen waarin je op de knop van de extensie hebt geklikt, totdat ze naar een andere site gaan.
fg_allow_all_sites|Op alle sites toestaan
extName|StreamRemaster
extDescription|Live-ondertitels voor elk tabblad, getranscribeerd en vertaald door je eigen Whisper-server.
start|Ondertitels aan
stop|Ondertitels uit
status_idle|Klaar
status_connecting|Verbinden…
status_loading|Model laden…
status_listening|Luisteren…
status_live|Live
status_stalled|Audio gestopt
status_error|Fout
status_noresponse|Geen antwoord
model|Transcriptiemodel
model_server_default|Dat van de server
model_default_tag|{0} · standaard
manage_models|Modellen beheren
spoken_lang|Taal van de audio
auto_detect|Automatisch
detected|Herkend: {0}
subs_lang|Ondertitels in
original_lang|Geen vertaling
lines|Regels
text_size|Tekstgrootte
save_srt|Ondertitels (.srt) opslaan bij het stoppen
advanced|Geavanceerd
use_vad|Stiltes overslaan (stemdetectie)
settings|Instellingen
first_load_hint|De eerste keer kan het laden van een model tot een minuut duren.
options_locked|Zet de ondertitels uit om deze opties te wijzigen.
server_setup_title|Verbind je server
server_setup_hint|StreamRemaster transcribeert met een WhisperLive-server op je computer of in je netwerk, of met de videokaart van deze computer.
server_address|Serveradres
server_placeholder|bijv. localhost:9090 of 192.168.1.10:9090
connect|Verbinden
server_ok_models|Verbonden · {0} modellen
server_ok_one_model|Verbonden · 1 model
server_plain|Verbonden · standaard WhisperLive (zonder modelbeheer)
server_checking|Controleren…
server_unreachable|De server is niet bereikbaar. Staat hij aan? Controleer het adres en de firewall.
server_timeout|De server antwoordde niet op tijd.
server_bad_url|Dat adres is ongeldig.
server_change|Wijzigen
server_help|Hoe zet ik een server op?
server_help_1|Je hebt een WhisperLive-server nodig (vrij en gratis) op een computer, liefst met een NVIDIA-videokaart. Kleine modellen werken ook alleen op de processor.
server_help_2|Typ hier daarna zijn adres: het IP van de computer en de poort, bijv. 192.168.1.10:9090. Draait hij op deze computer, dan localhost:9090.
server_help_3|Om vanaf deze pagina modellen te downloaden en te beheren, voeg je de StreamRemaster-add-on toe aan de server.
server_help_guide|Stapsgewijze handleiding
error_capture|Dit tabblad kan niet worden opgenomen (browserpagina’s, extensiewinkels en pdf’s zijn uitgesloten).
error_no_media|Er staat geen video of audio op deze pagina.
error_server_full|De server is bezet. Geschatte wachttijd: {0} min.
error_disconnected|De server heeft de verbinding gesloten.
error_model_load|⚠ Er is te weinig grafisch geheugen (VRAM) op de server voor dit model. Kies een kleiner model of zet ‘Geheugen besparen (int8)’ aan bij Geavanceerd.
warn_no_response|⚠ Er komen geen ondertitels meer, al is er geluid. Waarschijnlijk past het model niet in het grafische geheugen (VRAM) van de server: kies een kleiner model of zet ‘Geheugen besparen (int8)’ aan bij Geavanceerd.
warn_slow_load|⚠ Het laden van het model duurt te lang. Misschien past het niet in het grafische geheugen (VRAM) van de server: kies een kleiner model of zet ‘Geheugen besparen (int8)’ aan bij Geavanceerd.
error_reload|Herlaad de pagina (F5) en begin opnieuw.
error_no_server|Stel eerst de server in.
settings_title|StreamRemaster · Instellingen
section_subtitles|Ondertitels
section_interface|Interface
section_about|Over
installed_models|Geïnstalleerd op de server
no_models|Nog geen modellen geïnstalleerd.
badge_default|Standaard
badge_loaded|In geheugen
badge_selected|Gekozen
use_model|Gebruiken
delete_model|Verwijderen
confirm_delete|{0} van de server verwijderen? Dat maakt {1} vrij.
add_model|Een model toevoegen
add_model_hint|Plak de naam of de link van een model op Hugging Face. Elk Whisper-model werkt: faster-whisper-modellen (CTranslate2) worden zo gebruikt en gewone (transformers) automatisch omgezet. Een directe link naar een .zip of .tar.gz met een model werkt ook.
add_model_placeholder|bijv. Systran/faster-whisper-large-v3
download|Downloaden
suggestions|Suggesties:
browse_hf|Whisper-modellen op Hugging Face bekijken
vram_hint|Grotere modellen zijn nauwkeuriger maar vragen meer videogeheugen: small ≈ 1 GB, medium ≈ 2 GB, large ≈ 4 GB.
keep_open|Laat deze pagina open tot de download klaar is.
job_downloading|Downloaden… {0} van {1}
job_downloading_nosize|Downloaden… {0}
job_converting|Omzetten naar het faster-whisper-formaat…
job_extracting|Uitpakken…
job_ready|Geïnstalleerd
job_error|Mislukt: {0}
retry|Opnieuw
plain_server_hint|Dit is een standaard WhisperLive-server: typ een modelgrootte (tiny, base, small, medium, large-v3, large-v3-turbo) en de server downloadt die de eerste keer. Om elk model vanaf hier te downloaden, installeer je de StreamRemaster-add-on op de server.
model_name|Modelnaam
save|Opslaan
saved|Opgeslagen
reset_position|Positie van ondertitels herstellen
position_reset_done|Klaar: ze gaan weer naar onderen.
section_performance|Prestaties
performance_hint|Als de videokaart van de server zonder geheugen komt (ondertitels die niet komen of een geheugenwaarschuwing), maken deze twee opties veel vrij. Ze werken alleen met de StreamRemaster-server.
precision|Modelprecisie
precision_auto|Automatisch
precision_int8|Geheugen besparen (int8)
precision_hint|int8 gebruikt ongeveer de helft van het videogeheugen en schrijft in de praktijk dezelfde tekst.
translator_device|De vertaler draait op
device_gpu|Videokaart
device_cpu|Processor (CPU)
translator_device_hint|Op de processor komt videogeheugen vrij, maar vertaalde ondertitels komen iets later.
interface_lang|Taal van de interface
lang_auto|Die van de browser
about_text|Broncode beschikbaar (PolyForm Noncommercial-licentie). De audio gaat alleen naar de server die je hier instelt; er wordt niets ergens anders heen gestuurd.
about_based|Gebaseerd op WhisperLive van Collabora.
source_code|Broncode
subtitle_preview|Zo zien je ondertitels eruit.
err_invalid_source|Dat is geen modelnaam van Hugging Face en geen link.
err_unsupported_url|Alleen links van Hugging Face of directe links naar .zip-/.tar.gz-bestanden.
err_repo_not_found|Dat model bestaat niet op Hugging Face (controleer de naam).
err_gated_repo|Voor dat model moet je de voorwaarden op Hugging Face accepteren; de server heeft een HF_TOKEN nodig.
err_not_whisper|Dat is geen Whisper-model.
err_no_weights|Die repository bevat geen modelgewichten.
err_network_error|Netwerkfout. Probeer opnieuw: het gaat verder waar het stopte.
err_download_failed|De download is mislukt.
err_convert_failed|Het model kon niet worden omgezet.
err_bad_archive|Het archief is beschadigd of onveilig.
err_already_downloading|Het wordt al gedownload.
err_already_installed|Het is al geïnstalleerd.
err_management_disabled|Modelbeheer staat uit op deze server.
err_is_default|Dat is het standaardmodel van de server; het kan hier niet worden verwijderd.
err_in_use|Een lopende transcriptie gebruikt het.
err_not_found|Dat model staat niet meer op de server.
err_server_error|Serverfout.
err_unreachable|De server is niet bereikbaar.
err_timeout|De server antwoordde niet op tijd.
err_unknown|Onverwachte fout ({0}).
updates|Updates
check_updates|Controleren op updates
check_again|Opnieuw controleren
update_now|Bijwerken
update_available|Versie {0} is beschikbaar (je hebt {1}).
update_latest|Je hebt de nieuwste versie ({0}).
update_rate_limited|GitHub beperkt de controles een tijdje. Probeer het later opnieuw.
update_failed|Kon niet op updates controleren. Controleer de verbinding en probeer het opnieuw.
update_how_firefox|Firefox installeert nieuwe versies zelf. Wil je hem nu al, open dan about:addons, klik op het tandwiel en kies ‘Controleren op updates’. Een net verschenen versie kan een paar dagen nodig hebben om op de add-onsite te komen.
update_how_chromium|Om bij te werken download je de Chromium-zip van de pagina van de versie, pak je hem uit over de oude map en klik je in chrome://extensions op het herlaadpictogram op de kaart van StreamRemaster. Je instellingen blijven bewaard.
update_privacy|Bij het controleren wordt GitHub alleen naar het nummer van de nieuwste versie gevraagd; verder wordt er niets verstuurd.
server_update_available|Je server heeft versie {0} en {1} is beschikbaar. Voer dit uit op de computer waarop hij draait om hem bij te werken:
server_version_unknown|Je server zegt niet welke versie hij heeft, dus hij is ouder dan deze controle. Voer dit uit op de computer waarop hij draait om hem bij te werken:
server_update_latest|Je server is bijgewerkt ({0}).
server_update_note|De modellen blijven in het Docker-volume en worden niet opnieuw gedownload. Als je docker-compose.yml hebt aangepast en git pull klaagt, voer dan eerst git stash uit en daarna git stash pop.
setup_or|of
use_local|Deze computer gebruiken
use_local_hint|Whisper draait op de videokaart van deze computer, zonder server. Je downloadt het model één keer, in Instellingen.
local_footer|Deze computer
local_none|Nog geen model: download er een
local_intro|Whisper draait in de browser, op je videokaart (WebGPU). Elk model wordt één keer van Hugging Face gedownload en blijft in de browser. De grotere schrijven beter en hebben meer videogeheugen nodig.
local_sizes|Download {0} · neemt {1} in · ongeveer {2} videogeheugen
local_progress|Downloaden… {0} van {1}
local_cancel|Annuleren
local_gpu|Videokaart: {0}
badge_downloaded|Gedownload
error_no_webgpu|Deze browser kan de videokaart (WebGPU) niet gebruiken, dus kan hij niet op deze computer transcriberen.
error_local_missing|Download eerst een model, in Instellingen → Modellen op deze computer.
error_local_failed|Het transcriberen op deze computer is gestopt door een fout.
error_local_vram|⚠ Niet genoeg videogeheugen op deze computer voor dit model. Kies een kleiner model.
local_download_failed|Het downloaden is mislukt ({0}).
local_confirm_delete|Model {0} van deze computer verwijderen? Dat maakt {1} vrij.
local_only_english|Op deze computer kunnen de ondertitels alleen naar het Engels worden vertaald.
"""

LANGS['pl'] = """
error_local_lost|Karta graficzna kilka razy z rzędu zatrzymała model transkrypcji.
fg_hq_badge|Dla mocnych kart graficznych
where_fg_models|Gdzie są modele
fg_local_title|Modele płynnego wideo na tym komputerze
fg_server_title|Modele płynnego wideo na serwerze
fg_server_intro|Serwer tylko je przechowuje: wybrany model pobiera się z niego i działa na karcie graficznej tego komputera.
fg_server_none|Serwer nie ma jeszcze modeli płynnego wideo.
fg_server_old|Ten serwer nie przechowuje modeli płynnego wideo: zaktualizuj go do najnowszej wersji.
fg_add_server_title|Dodaj do serwera
fg_server_loading|Pobieranie modelu z serwera…
section_transcription|Modele transkrypcji
transcription_intro|Wybierz, gdzie mowa zamienia się w tekst: na serwerze WhisperLive czy na karcie graficznej tego komputera.
where_transcribe|Gdzie transkrybować
engine_server|Na serwerze
engine_local|Na tym komputerze
trans_server_title|Modele transkrypcji na serwerze
trans_local_title|Modele transkrypcji na tym komputerze
badge_in_use|W użyciu
fg_downloaded_title|Pobrane
fg_add_title|Dodaj model
fg_add_url_placeholder|Adres pliku modelu (.stmodel)
fg_download_failed|Nie udało się pobrać ({0}). Pobierz plik przeglądarką i wybierz go z tego komputera.
fg_memory|Pamięć karty graficznej: około {0} przy filmie 1080p
fg_memory_4k|około {0} przy skalowaniu z 1080p do 4K
fg_memory_now|Używana pamięć karty graficznej: około {0}
fg_file_size|Plik: {0}
fg_options|Opcje
fg_sharpen|Ostrość
fg_sharpen_off|Wyłączona
fg_sharpen_soft|Łagodna
fg_sharpen_medium|Średnia
fg_sharpen_strong|Mocna
fg_resolution|Docelowa rozdzielczość skalowania
fg_res_original|Oryginalna (bez skalowania)
fg_model|Model płynnego wideo
fg_kind_sr|Tylko skalowanie
fg_kind_fi|Tylko klatki pośrednie
fg_builtin|Wbudowany
fg_model_none|Brak (bez AI)
section_fgmodels|Modele płynnego wideo
fg_models_hint|Płynne wideo zawsze działa na karcie graficznej tego komputera. StreamRemaster jest dołączony do rozszerzenia; inne modele mogą być na tym komputerze lub na twoim serwerze.
fg_add_model|Wybierz plik z tego komputera
fg_no_models|Brak pobranych modeli.
fg_model_bad|Ten plik nie jest prawidłowym modelem.
tab_subs|Napisy
tab_fg|Płynne wideo
fg_start|Włącz płynne wideo
fg_stop|Wyłącz płynne wideo
fg_target|Docelowe FPS
fg_target_display|Jak ekran
fg_state_off|Wyłączone
fg_state_measuring|Pomiar wideo…
fg_state_on|{0} fps (wideo {1} fps)
fg_no_video|Na tej stronie nie jest odtwarzane żadne wideo.
fg_no_webgpu|Ta przeglądarka nie może użyć do tego GPU (WebGPU jest niedostępne).
fg_cannot_read|Nie można odczytać tego wideo: jest chronione lub pochodzi z innej witryny.
fg_unavailable|Ta strona nie zezwala na rozszerzenia.
fg_auto_start|Włączaj płynne wideo, gdy odtwarzany jest film
subs_auto_start|Uruchamiaj napisy, gdy odtwarzany jest film
auto_start_hint|W tej przeglądarce działa to tylko na kartach, na których kliknięto przycisk rozszerzenia, dopóki nie przejdą na inną stronę.
fg_allow_all_sites|Zezwól na wszystkich stronach
extName|StreamRemaster
extDescription|Napisy na żywo w dowolnej karcie, transkrybowane i tłumaczone przez twój własny serwer Whisper.
start|Włącz napisy
stop|Wyłącz napisy
status_idle|Gotowe
status_connecting|Łączenie…
status_loading|Wczytywanie modelu…
status_listening|Nasłuchiwanie…
status_live|Na żywo
status_stalled|Dźwięk zatrzymany
status_error|Błąd
status_noresponse|Brak odpowiedzi
model|Model transkrypcji
model_server_default|Domyślny serwera
model_default_tag|{0} · domyślny
manage_models|Zarządzaj modelami
spoken_lang|Język dźwięku
auto_detect|Automatycznie
detected|Wykryto: {0}
subs_lang|Napisy w języku
original_lang|Bez tłumaczenia
lines|Wiersze
text_size|Rozmiar tekstu
save_srt|Zapisz napisy (.srt) po zatrzymaniu
advanced|Zaawansowane
use_vad|Pomijaj ciszę (wykrywanie mowy)
settings|Ustawienia
first_load_hint|Za pierwszym razem wczytanie modelu może potrwać do minuty.
options_locked|Wyłącz napisy, aby zmienić te opcje.
server_setup_title|Połącz swój serwer
server_setup_hint|StreamRemaster transkrybuje za pomocą serwera WhisperLive na twoim komputerze lub w twojej sieci albo karty graficznej tego komputera.
server_address|Adres serwera
server_placeholder|np. localhost:9090 lub 192.168.1.10:9090
connect|Połącz
server_ok_models|Połączono · modele: {0}
server_ok_one_model|Połączono · 1 model
server_plain|Połączono · standardowy WhisperLive (bez zarządzania modelami)
server_checking|Sprawdzanie…
server_unreachable|Nie można połączyć się z serwerem. Czy jest włączony? Sprawdź adres i zaporę.
server_timeout|Serwer nie odpowiedział na czas.
server_bad_url|Ten adres jest nieprawidłowy.
server_change|Zmień
server_help|Jak skonfigurować serwer?
server_help_1|Potrzebujesz serwera WhisperLive (wolnego i darmowego) na komputerze, najlepiej z kartą graficzną NVIDIA. Małe modele działają też na samym procesorze.
server_help_2|Potem wpisz tu jego adres: IP komputera i port, np. 192.168.1.10:9090. Jeśli działa na tym komputerze — localhost:9090.
server_help_3|Aby pobierać modele i zarządzać nimi z tej strony, dodaj do serwera dodatek StreamRemaster.
server_help_guide|Przewodnik krok po kroku
error_capture|Tej karty nie można przechwycić (strony przeglądarki, sklepy z rozszerzeniami i pliki PDF są wykluczone).
error_no_media|Na tej stronie nie ma wideo ani dźwięku.
error_server_full|Serwer jest zajęty. Szacowany czas oczekiwania: {0} min.
error_disconnected|Serwer zamknął połączenie.
error_model_load|⚠ Serwer ma za mało pamięci graficznej (VRAM) na ten model. Wybierz mniejszy model lub włącz „Oszczędzaj pamięć (int8)” w Zaawansowanych.
warn_no_response|⚠ Napisy przestały przychodzić, choć jest dźwięk. Model pewnie nie mieści się w pamięci graficznej (VRAM) serwera: wybierz mniejszy model lub włącz „Oszczędzaj pamięć (int8)” w Zaawansowanych.
warn_slow_load|⚠ Model wczytuje się za długo. Może nie mieścić się w pamięci graficznej (VRAM) serwera: wybierz mniejszy model lub włącz „Oszczędzaj pamięć (int8)” w Zaawansowanych.
error_reload|Odśwież stronę (F5) i zacznij od nowa.
error_no_server|Najpierw skonfiguruj serwer.
settings_title|StreamRemaster · Ustawienia
section_subtitles|Napisy
section_interface|Interfejs
section_about|Informacje
installed_models|Zainstalowane na serwerze
no_models|Nie ma jeszcze zainstalowanych modeli.
badge_default|Domyślny
badge_loaded|W pamięci
badge_selected|Wybrany
use_model|Użyj
delete_model|Usuń
confirm_delete|Usunąć {0} z serwera? Zwolni to {1}.
add_model|Dodaj model
add_model_hint|Wklej nazwę lub link modelu z Hugging Face. Pasuje każdy model Whisper: modele faster-whisper (CTranslate2) są używane bez zmian, a zwykłe (transformers) konwertowane automatycznie. Działa też bezpośredni link do pliku .zip lub .tar.gz z modelem.
add_model_placeholder|np. Systran/faster-whisper-large-v3
download|Pobierz
suggestions|Propozycje:
browse_hf|Zobacz modele Whisper na Hugging Face
vram_hint|Większe modele są dokładniejsze, ale potrzebują więcej pamięci karty graficznej: small ≈ 1 GB, medium ≈ 2 GB, large ≈ 4 GB.
keep_open|Nie zamykaj tej strony, dopóki pobieranie się nie skończy.
job_downloading|Pobieranie… {0} z {1}
job_downloading_nosize|Pobieranie… {0}
job_converting|Konwersja do formatu faster-whisper…
job_extracting|Rozpakowywanie…
job_ready|Zainstalowano
job_error|Niepowodzenie: {0}
retry|Spróbuj ponownie
plain_server_hint|To standardowy serwer WhisperLive: wpisz rozmiar modelu (tiny, base, small, medium, large-v3, large-v3-turbo), a serwer pobierze go za pierwszym razem. Aby pobierać stąd dowolne modele, zainstaluj na serwerze dodatek StreamRemaster.
model_name|Nazwa modelu
save|Zapisz
saved|Zapisano
reset_position|Przywróć położenie napisów
position_reset_done|Gotowe: wrócą na dół.
section_performance|Wydajność
performance_hint|Jeśli karcie graficznej serwera brakuje pamięci (napisy nie przychodzą albo pojawia się ostrzeżenie o pamięci), te dwie opcje sporo jej zwalniają. Działają tylko z serwerem StreamRemaster.
precision|Precyzja modelu
precision_auto|Automatyczna
precision_int8|Oszczędzaj pamięć (int8)
precision_hint|int8 zużywa mniej więcej połowę pamięci graficznej i w praktyce pisze ten sam tekst.
translator_device|Tłumacz działa na
device_gpu|Karcie graficznej
device_cpu|Procesorze (CPU)
translator_device_hint|Na procesorze zwalnia pamięć graficzną, ale przetłumaczone napisy przychodzą nieco później.
interface_lang|Język interfejsu
lang_auto|Jak w przeglądarce
about_text|Kod źródłowy dostępny (licencja PolyForm Noncommercial). Dźwięk trafia tylko do serwera, który tu skonfigurujesz; nic nie jest wysyłane nigdzie indziej.
about_based|Oparte na WhisperLive od Collabora.
source_code|Kod źródłowy
subtitle_preview|Tak będą wyglądać twoje napisy.
err_invalid_source|To nie jest nazwa modelu z Hugging Face ani link.
err_unsupported_url|Tylko linki do Hugging Face lub bezpośrednie linki do plików .zip / .tar.gz.
err_repo_not_found|Taki model nie istnieje na Hugging Face (sprawdź nazwę).
err_gated_repo|Ten model wymaga zaakceptowania warunków na Hugging Face; serwer potrzebuje HF_TOKEN.
err_not_whisper|To nie jest model Whisper.
err_no_weights|To repozytorium nie zawiera wag modelu.
err_network_error|Błąd sieci. Spróbuj ponownie: zacznie od miejsca, w którym przerwał.
err_download_failed|Pobieranie nie powiodło się.
err_convert_failed|Nie udało się przekonwertować modelu.
err_bad_archive|Archiwum jest uszkodzone lub niebezpieczne.
err_already_downloading|Już się pobiera.
err_already_installed|Już jest zainstalowany.
err_management_disabled|Zarządzanie modelami jest wyłączone na tym serwerze.
err_is_default|To domyślny model serwera; nie można go stąd usunąć.
err_in_use|Używa go trwająca transkrypcja.
err_not_found|Tego modelu nie ma już na serwerze.
err_server_error|Błąd serwera.
err_unreachable|Nie można połączyć się z serwerem.
err_timeout|Serwer nie odpowiedział na czas.
err_unknown|Nieoczekiwany błąd ({0}).
updates|Aktualizacje
check_updates|Sprawdź aktualizacje
check_again|Sprawdź ponownie
update_now|Aktualizuj
update_available|Dostępna jest wersja {0} (masz {1}).
update_latest|Masz najnowszą wersję ({0}).
update_rate_limited|GitHub przez jakiś czas ogranicza sprawdzanie. Spróbuj ponownie później.
update_failed|Nie udało się sprawdzić aktualizacji. Sprawdź połączenie i spróbuj ponownie.
update_how_firefox|Firefox sam instaluje nowe wersje. Aby mieć ją od razu, otwórz about:addons, kliknij ikonę koła zębatego i wybierz „Sprawdź dostępność aktualizacji”. Świeżo wydana wersja może dotrzeć do witryny dodatków dopiero po kilku dniach.
update_how_chromium|Aby zaktualizować, pobierz plik zip dla Chromium ze strony wersji, rozpakuj go na starym folderze i kliknij ikonę ponownego wczytania na karcie StreamRemaster w chrome://extensions. Ustawienia zostają zachowane.
update_privacy|Sprawdzanie tylko pyta GitHub o numer najnowszej wersji; nic więcej nie jest wysyłane.
server_update_available|Twój serwer ma wersję {0}, a dostępna jest {1}. Aby go zaktualizować, uruchom to na komputerze, na którym działa:
server_version_unknown|Twój serwer nie podaje swojej wersji, więc jest starszy niż to sprawdzanie. Aby go zaktualizować, uruchom to na komputerze, na którym działa:
server_update_latest|Twój serwer jest aktualny ({0}).
server_update_note|Modele zostają w woluminie Dockera i nie są pobierane ponownie. Jeśli plik docker-compose.yml był zmieniany, a git pull zgłasza błąd, uruchom przed nim git stash, a po nim git stash pop.
setup_or|lub
use_local|Użyj tego komputera
use_local_hint|Whisper działa na karcie graficznej tego komputera, bez serwera. Model pobierasz raz, w Ustawieniach.
local_footer|Ten komputer
local_none|Brak modelu: pobierz jakiś
local_intro|Whisper działa w przeglądarce, na Twojej karcie graficznej (WebGPU). Każdy model pobiera się raz z Hugging Face i zostaje w przeglądarce. Większe piszą lepiej i potrzebują więcej pamięci graficznej.
local_sizes|Pobieranie {0} · zajmuje {1} · około {2} pamięci graficznej
local_progress|Pobieranie… {0} z {1}
local_cancel|Anuluj
local_gpu|Karta graficzna: {0}
badge_downloaded|Pobrany
error_no_webgpu|Ta przeglądarka nie może używać karty graficznej (WebGPU), więc nie może transkrybować na tym komputerze.
error_local_missing|Najpierw pobierz model w Ustawienia → Modele na tym komputerze.
error_local_failed|Transkrypcja na tym komputerze zatrzymała się z powodu błędu.
error_local_vram|⚠ Za mało pamięci graficznej na tym komputerze dla tego modelu. Wybierz mniejszy.
local_download_failed|Pobieranie nie powiodło się ({0}).
local_confirm_delete|Usunąć model {0} z tego komputera? Zwolni {1}.
local_only_english|Na tym komputerze napisy można tłumaczyć tylko na angielski.
"""

LANGS['ru'] = """
error_local_lost|Видеокарта несколько раз подряд остановила модель распознавания.
fg_hq_badge|Для мощных видеокарт
where_fg_models|Где хранятся модели
fg_local_title|Модели плавного видео на этом компьютере
fg_server_title|Модели плавного видео на сервере
fg_server_intro|Сервер только хранит их: выбранная модель скачивается с него и работает на видеокарте этого компьютера.
fg_server_none|На сервере пока нет моделей плавного видео.
fg_server_old|Этот сервер не хранит модели плавного видео: обновите его до последней версии.
fg_add_server_title|Добавить на сервер
fg_server_loading|Загрузка модели с сервера…
section_transcription|Модели распознавания речи
transcription_intro|Выберите, где речь превращается в текст: на сервере WhisperLive или на видеокарте этого компьютера.
where_transcribe|Где распознавать
engine_server|На сервере
engine_local|На этом компьютере
trans_server_title|Модели распознавания на сервере
trans_local_title|Модели распознавания на этом компьютере
badge_in_use|Используется
fg_downloaded_title|Загруженные
fg_add_title|Добавить модель
fg_add_url_placeholder|Адрес файла модели (.stmodel)
fg_download_failed|Не удалось загрузить ({0}). Скачайте файл через браузер и выберите его на этом компьютере.
fg_memory|Видеопамять: около {0} для видео 1080p
fg_memory_4k|около {0} при масштабировании с 1080p до 4K
fg_memory_now|Занято видеопамяти: около {0}
fg_file_size|Файл: {0}
fg_options|Параметры
fg_sharpen|Резкость
fg_sharpen_off|Выключена
fg_sharpen_soft|Слабая
fg_sharpen_medium|Средняя
fg_sharpen_strong|Сильная
fg_resolution|Целевое разрешение масштабирования
fg_res_original|Исходное (без масштабирования)
fg_model|Модель плавного видео
fg_kind_sr|Только масштабирование
fg_kind_fi|Только промежуточные кадры
fg_builtin|Встроенная
fg_model_none|Нет (без ИИ)
section_fgmodels|Модели плавного видео
fg_models_hint|Плавное видео всегда работает на видеокарте этого компьютера. StreamRemaster входит в расширение; другие модели могут быть на этом компьютере или на вашем сервере.
fg_add_model|Выбрать файл на этом компьютере
fg_no_models|Загруженных моделей пока нет.
fg_model_bad|Этот файл не является допустимой моделью.
tab_subs|Субтитры
tab_fg|Плавное видео
fg_start|Включить плавное видео
fg_stop|Выключить плавное видео
fg_target|Целевая частота кадров
fg_target_display|Как у экрана
fg_state_off|Выключено
fg_state_measuring|Измерение видео…
fg_state_on|{0} к/с (видео {1} к/с)
fg_no_video|На этой странице не воспроизводится видео.
fg_no_webgpu|Этот браузер не может использовать для этого видеокарту (WebGPU недоступен).
fg_cannot_read|Это видео нельзя прочитать: оно защищено или загружено с другого сайта.
fg_unavailable|Эта страница не разрешает расширения.
fg_auto_start|Включать плавное видео при воспроизведении видео
subs_auto_start|Запускать субтитры при воспроизведении видео
auto_start_hint|В этом браузере это работает только во вкладках, где вы нажали кнопку расширения, пока они не перейдут на другой сайт.
fg_allow_all_sites|Разрешить на всех сайтах
extName|StreamRemaster
extDescription|Субтитры в реальном времени для любой вкладки: распознаёт и переводит ваш собственный сервер Whisper.
start|Включить субтитры
stop|Выключить субтитры
status_idle|Готово
status_connecting|Подключение…
status_loading|Загрузка модели…
status_listening|Слушаю…
status_live|В эфире
status_stalled|Звук остановлен
status_error|Ошибка
status_noresponse|Нет ответа
model|Модель распознавания
model_server_default|Как на сервере
model_default_tag|{0} · по умолчанию
manage_models|Управлять моделями
spoken_lang|Язык аудио
auto_detect|Автоматически
detected|Определён: {0}
subs_lang|Субтитры на
original_lang|Без перевода
lines|Строки
text_size|Размер текста
save_srt|Сохранять субтитры (.srt) при остановке
advanced|Дополнительно
use_vad|Пропускать тишину (обнаружение речи)
settings|Настройки
first_load_hint|В первый раз загрузка модели может занять до минуты.
options_locked|Выключите субтитры, чтобы изменить эти параметры.
server_setup_title|Подключите свой сервер
server_setup_hint|StreamRemaster распознаёт речь с помощью сервера WhisperLive на вашем компьютере или в сети либо на видеокарте этого компьютера.
server_address|Адрес сервера
server_placeholder|напр. localhost:9090 или 192.168.1.10:9090
connect|Подключить
server_ok_models|Подключено · моделей: {0}
server_ok_one_model|Подключено · 1 модель
server_plain|Подключено · стандартный WhisperLive (без управления моделями)
server_checking|Проверка…
server_unreachable|Не удаётся связаться с сервером. Он включён? Проверьте адрес и брандмауэр.
server_timeout|Сервер не ответил вовремя.
server_bad_url|Этот адрес недействителен.
server_change|Изменить
server_help|Как настроить сервер?
server_help_1|Нужен сервер WhisperLive (свободный и бесплатный) на компьютере, лучше с видеокартой NVIDIA. Небольшие модели работают и на одном процессоре.
server_help_2|Затем введите здесь его адрес: IP компьютера и порт, напр. 192.168.1.10:9090. Если он на этом же компьютере — localhost:9090.
server_help_3|Чтобы скачивать модели и управлять ими с этой страницы, добавьте на сервер дополнение StreamRemaster.
server_help_guide|Пошаговое руководство
error_capture|Эту вкладку нельзя захватить (страницы браузера, магазины расширений и PDF недоступны).
error_no_media|На этой странице нет ни видео, ни звука.
error_server_full|Сервер занят. Примерное ожидание: {0} мин.
error_disconnected|Сервер закрыл соединение.
error_model_load|⚠ На сервере не хватает видеопамяти (VRAM) для этой модели. Выберите модель поменьше или включите «Экономить память (int8)» в разделе «Дополнительно».
warn_no_response|⚠ Субтитры перестали приходить, хотя звук есть. Вероятно, модель не помещается в видеопамять (VRAM) сервера: выберите модель поменьше или включите «Экономить память (int8)» в разделе «Дополнительно».
warn_slow_load|⚠ Модель загружается слишком долго. Возможно, она не помещается в видеопамять (VRAM) сервера: выберите модель поменьше или включите «Экономить память (int8)» в разделе «Дополнительно».
error_reload|Перезагрузите страницу (F5) и начните заново.
error_no_server|Сначала настройте сервер.
settings_title|StreamRemaster · Настройки
section_subtitles|Субтитры
section_interface|Интерфейс
section_about|О программе
installed_models|Установлены на сервере
no_models|Моделей пока нет.
badge_default|По умолчанию
badge_loaded|В памяти
badge_selected|Выбрана
use_model|Использовать
delete_model|Удалить
confirm_delete|Удалить {0} с сервера? Освободится {1}.
add_model|Добавить модель
add_model_hint|Вставьте название или ссылку на модель с Hugging Face. Подойдёт любая модель Whisper: модели faster-whisper (CTranslate2) используются как есть, обычные (transformers) конвертируются автоматически. Подойдёт и прямая ссылка на .zip или .tar.gz с моделью.
add_model_placeholder|напр. Systran/faster-whisper-large-v3
download|Скачать
suggestions|Варианты:
browse_hf|Смотреть модели Whisper на Hugging Face
vram_hint|Большие модели точнее, но им нужно больше видеопамяти: small ≈ 1 ГБ, medium ≈ 2 ГБ, large ≈ 4 ГБ.
keep_open|Не закрывайте эту страницу, пока скачивание не закончится.
job_downloading|Скачивание… {0} из {1}
job_downloading_nosize|Скачивание… {0}
job_converting|Конвертация в формат faster-whisper…
job_extracting|Распаковка…
job_ready|Установлена
job_error|Не удалось: {0}
retry|Повторить
plain_server_hint|Это стандартный сервер WhisperLive: введите размер модели (tiny, base, small, medium, large-v3, large-v3-turbo), и сервер скачает её при первом запуске. Чтобы скачивать отсюда любые модели, установите на сервер дополнение StreamRemaster.
model_name|Название модели
save|Сохранить
saved|Сохранено
reset_position|Сбросить положение субтитров
position_reset_done|Готово: они вернутся вниз.
section_performance|Производительность
performance_hint|Если видеокарте сервера не хватает памяти (субтитры не приходят или появляется предупреждение о памяти), эти два параметра освобождают немало. Работают только с сервером StreamRemaster.
precision|Точность модели
precision_auto|Автоматически
precision_int8|Экономить память (int8)
precision_hint|int8 занимает примерно половину видеопамяти и на практике пишет тот же текст.
translator_device|Переводчик работает на
device_gpu|Видеокарте
device_cpu|Процессоре (CPU)
translator_device_hint|На процессоре освобождается видеопамять, но переведённые субтитры приходят чуть позже.
interface_lang|Язык интерфейса
lang_auto|Как в браузере
about_text|Исходный код доступен (лицензия PolyForm Noncommercial). Звук идёт только на сервер, который вы здесь укажете; больше никуда ничего не отправляется.
about_based|Основано на WhisperLive от Collabora.
source_code|Исходный код
subtitle_preview|Так будут выглядеть ваши субтитры.
err_invalid_source|Это не название модели Hugging Face и не ссылка.
err_unsupported_url|Только ссылки на Hugging Face или прямые ссылки на файлы .zip / .tar.gz.
err_repo_not_found|Такой модели на Hugging Face нет (проверьте название).
err_gated_repo|Для этой модели нужно принять условия на Hugging Face; серверу нужен HF_TOKEN.
err_not_whisper|Это не модель Whisper.
err_no_weights|В этом репозитории нет весов модели.
err_network_error|Ошибка сети. Повторите: продолжит с того места, где остановилось.
err_download_failed|Скачивание не удалось.
err_convert_failed|Не удалось конвертировать модель.
err_bad_archive|Архив повреждён или небезопасен.
err_already_downloading|Уже скачивается.
err_already_installed|Уже установлена.
err_management_disabled|Управление моделями на этом сервере выключено.
err_is_default|Это модель сервера по умолчанию; удалить её отсюда нельзя.
err_in_use|Её использует идущая транскрипция.
err_not_found|Этой модели на сервере больше нет.
err_server_error|Ошибка сервера.
err_unreachable|Не удаётся связаться с сервером.
err_timeout|Сервер не ответил вовремя.
err_unknown|Непредвиденная ошибка ({0}).
updates|Обновления
check_updates|Проверить обновления
check_again|Проверить ещё раз
update_now|Обновить
update_available|Доступна версия {0} (у вас {1}).
update_latest|У вас последняя версия ({0}).
update_rate_limited|GitHub временно ограничивает проверки. Попробуйте позже.
update_failed|Не удалось проверить обновления. Проверьте подключение и попробуйте ещё раз.
update_how_firefox|Firefox сам устанавливает новые версии. Чтобы получить её сразу, откройте about:addons, нажмите на значок шестерёнки и выберите «Проверить наличие обновлений». Только что вышедшая версия может появиться на сайте дополнений через несколько дней.
update_how_chromium|Чтобы обновить, скачайте zip для Chromium со страницы версии, распакуйте его поверх старой папки и нажмите значок перезагрузки на карточке StreamRemaster в chrome://extensions. Настройки сохранятся.
update_privacy|При проверке у GitHub запрашивается только номер последней версии; больше ничего не отправляется.
server_update_available|На вашем сервере версия {0}, а доступна {1}. Чтобы обновить его, выполните это на компьютере, где он работает:
server_version_unknown|Ваш сервер не сообщает свою версию, значит, он старше этой проверки. Чтобы обновить его, выполните это на компьютере, где он работает:
server_update_latest|Ваш сервер обновлён ({0}).
server_update_note|Модели остаются в томе Docker и заново не скачиваются. Если вы меняли docker-compose.yml и git pull выдаёт ошибку, выполните git stash перед ним и git stash pop после.
setup_or|или
use_local|Использовать этот компьютер
use_local_hint|Whisper работает на видеокарте этого компьютера, без сервера. Модель скачивается один раз, в настройках.
local_footer|Этот компьютер
local_none|Модели нет: скачайте её
local_intro|Whisper работает в браузере, на вашей видеокарте (WebGPU). Каждая модель скачивается один раз с Hugging Face и остаётся в браузере. Большие модели пишут точнее и требуют больше видеопамяти.
local_sizes|Загрузка {0} · занимает {1} · около {2} видеопамяти
local_progress|Загрузка… {0} из {1}
local_cancel|Отмена
local_gpu|Видеокарта: {0}
badge_downloaded|Скачана
error_no_webgpu|Этот браузер не может использовать видеокарту (WebGPU), поэтому не может распознавать речь на этом компьютере.
error_local_missing|Сначала скачайте модель: Настройки → Модели на этом компьютере.
error_local_failed|Распознавание на этом компьютере остановилось из-за ошибки.
error_local_vram|⚠ На этом компьютере не хватает видеопамяти для этой модели. Выберите модель поменьше.
local_download_failed|Загрузка не удалась ({0}).
local_confirm_delete|Удалить модель {0} с этого компьютера? Освободится {1}.
local_only_english|На этом компьютере субтитры можно переводить только на английский.
"""

LANGS['uk'] = """
error_local_lost|Відеокарта кілька разів поспіль зупинила модель розпізнавання.
fg_hq_badge|Для потужних відеокарт
where_fg_models|Де зберігаються моделі
fg_local_title|Моделі плавного відео на цьому комп’ютері
fg_server_title|Моделі плавного відео на сервері
fg_server_intro|Сервер лише зберігає їх: вибрана модель завантажується з нього й працює на відеокарті цього комп’ютера.
fg_server_none|На сервері ще немає моделей плавного відео.
fg_server_old|Цей сервер не зберігає моделі плавного відео: оновіть його до останньої версії.
fg_add_server_title|Додати на сервер
fg_server_loading|Завантаження моделі з сервера…
section_transcription|Моделі розпізнавання мовлення
transcription_intro|Виберіть, де мовлення перетворюється на текст: на сервері WhisperLive чи на відеокарті цього комп’ютера.
where_transcribe|Де розпізнавати
engine_server|На сервері
engine_local|На цьому комп’ютері
trans_server_title|Моделі розпізнавання на сервері
trans_local_title|Моделі розпізнавання на цьому комп’ютері
badge_in_use|Використовується
fg_downloaded_title|Завантажені
fg_add_title|Додати модель
fg_add_url_placeholder|Адреса файлу моделі (.stmodel)
fg_download_failed|Не вдалося завантажити ({0}). Завантажте файл через браузер і виберіть його на цьому комп’ютері.
fg_memory|Відеопам’ять: близько {0} для відео 1080p
fg_memory_4k|близько {0} при масштабуванні з 1080p до 4K
fg_memory_now|Зайнято відеопам’яті: близько {0}
fg_file_size|Файл: {0}
fg_options|Параметри
fg_sharpen|Різкість
fg_sharpen_off|Вимкнено
fg_sharpen_soft|Слабка
fg_sharpen_medium|Середня
fg_sharpen_strong|Сильна
fg_resolution|Цільова роздільна здатність масштабування
fg_res_original|Початкова (без масштабування)
fg_model|Модель плавного відео
fg_kind_sr|Лише масштабування
fg_kind_fi|Лише проміжні кадри
fg_builtin|Вбудована
fg_model_none|Немає (без ШІ)
section_fgmodels|Моделі плавного відео
fg_models_hint|Плавне відео завжди працює на відеокарті цього комп’ютера. StreamRemaster входить до розширення; інші моделі можуть бути на цьому комп’ютері або на вашому сервері.
fg_add_model|Вибрати файл на цьому комп’ютері
fg_no_models|Завантажених моделей поки немає.
fg_model_bad|Цей файл не є дійсною моделлю.
tab_subs|Субтитри
tab_fg|Плавне відео
fg_start|Увімкнути плавне відео
fg_stop|Вимкнути плавне відео
fg_target|Цільова частота кадрів
fg_target_display|Як на екрані
fg_state_off|Вимкнено
fg_state_measuring|Вимірювання відео…
fg_state_on|{0} к/с (відео {1} к/с)
fg_no_video|На цій сторінці не відтворюється відео.
fg_no_webgpu|Цей браузер не може використовувати для цього відеокарту (WebGPU недоступний).
fg_cannot_read|Це відео неможливо прочитати: воно захищене або завантажене з іншого сайту.
fg_unavailable|Ця сторінка не дозволяє розширення.
fg_auto_start|Вмикати плавне відео під час відтворення відео
subs_auto_start|Запускати субтитри під час відтворення відео
auto_start_hint|У цьому браузері це працює лише у вкладках, де ви натиснули кнопку розширення, доки вони не перейдуть на інший сайт.
fg_allow_all_sites|Дозволити на всіх сайтах
extName|StreamRemaster
extDescription|Субтитри наживо для будь-якої вкладки: розпізнає й перекладає ваш власний сервер Whisper.
start|Увімкнути субтитри
stop|Вимкнути субтитри
status_idle|Готово
status_connecting|Підключення…
status_loading|Завантаження моделі…
status_listening|Слухаю…
status_live|Наживо
status_stalled|Звук зупинено
status_error|Помилка
status_noresponse|Немає відповіді
model|Модель розпізнавання
model_server_default|Як на сервері
model_default_tag|{0} · типова
manage_models|Керувати моделями
spoken_lang|Мова аудіо
auto_detect|Автоматично
detected|Визначено: {0}
subs_lang|Субтитри мовою
original_lang|Без перекладу
lines|Рядки
text_size|Розмір тексту
save_srt|Зберігати субтитри (.srt) під час зупинки
advanced|Додатково
use_vad|Пропускати тишу (виявлення мовлення)
settings|Налаштування
first_load_hint|Першого разу завантаження моделі може тривати до хвилини.
options_locked|Вимкніть субтитри, щоб змінити ці параметри.
server_setup_title|Підключіть свій сервер
server_setup_hint|StreamRemaster розпізнає мовлення за допомогою сервера WhisperLive на вашому комп’ютері чи в мережі або на відеокарті цього комп’ютера.
server_address|Адреса сервера
server_placeholder|напр. localhost:9090 або 192.168.1.10:9090
connect|Підключити
server_ok_models|Підключено · моделей: {0}
server_ok_one_model|Підключено · 1 модель
server_plain|Підключено · стандартний WhisperLive (без керування моделями)
server_checking|Перевірка…
server_unreachable|Не вдається зв’язатися із сервером. Він увімкнений? Перевірте адресу й брандмауер.
server_timeout|Сервер не відповів вчасно.
server_bad_url|Ця адреса недійсна.
server_change|Змінити
server_help|Як налаштувати сервер?
server_help_1|Потрібен сервер WhisperLive (вільний і безкоштовний) на комп’ютері, краще з відеокартою NVIDIA. Невеликі моделі працюють і на самому процесорі.
server_help_2|Потім введіть тут його адресу: IP комп’ютера й порт, напр. 192.168.1.10:9090. Якщо він на цьому ж комп’ютері — localhost:9090.
server_help_3|Щоб завантажувати моделі й керувати ними з цієї сторінки, додайте на сервер доповнення StreamRemaster.
server_help_guide|Покроковий посібник
error_capture|Цю вкладку неможливо захопити (сторінки браузера, крамниці розширень і PDF недоступні).
error_no_media|На цій сторінці немає ні відео, ні звуку.
error_server_full|Сервер зайнятий. Орієнтовне очікування: {0} хв.
error_disconnected|Сервер закрив з’єднання.
error_model_load|⚠ На сервері бракує відеопам’яті (VRAM) для цієї моделі. Виберіть меншу модель або ввімкніть «Заощаджувати пам’ять (int8)» у розділі «Додатково».
warn_no_response|⚠ Субтитри перестали надходити, хоча звук є. Імовірно, модель не вміщується у відеопам’ять (VRAM) сервера: виберіть меншу модель або ввімкніть «Заощаджувати пам’ять (int8)» у розділі «Додатково».
warn_slow_load|⚠ Модель завантажується надто довго. Можливо, вона не вміщується у відеопам’ять (VRAM) сервера: виберіть меншу модель або ввімкніть «Заощаджувати пам’ять (int8)» у розділі «Додатково».
error_reload|Перезавантажте сторінку (F5) і почніть знову.
error_no_server|Спершу налаштуйте сервер.
settings_title|StreamRemaster · Налаштування
section_subtitles|Субтитри
section_interface|Інтерфейс
section_about|Про програму
installed_models|Встановлені на сервері
no_models|Моделей ще немає.
badge_default|Типова
badge_loaded|У пам’яті
badge_selected|Вибрана
use_model|Використати
delete_model|Видалити
confirm_delete|Видалити {0} із сервера? Звільниться {1}.
add_model|Додати модель
add_model_hint|Вставте назву або посилання на модель із Hugging Face. Підійде будь-яка модель Whisper: моделі faster-whisper (CTranslate2) використовуються як є, звичайні (transformers) конвертуються автоматично. Підійде й пряме посилання на .zip або .tar.gz із моделлю.
add_model_placeholder|напр. Systran/faster-whisper-large-v3
download|Завантажити
suggestions|Варіанти:
browse_hf|Переглянути моделі Whisper на Hugging Face
vram_hint|Більші моделі точніші, але потребують більше відеопам’яті: small ≈ 1 ГБ, medium ≈ 2 ГБ, large ≈ 4 ГБ.
keep_open|Не закривайте цю сторінку, доки завантаження не завершиться.
job_downloading|Завантаження… {0} із {1}
job_downloading_nosize|Завантаження… {0}
job_converting|Конвертація у формат faster-whisper…
job_extracting|Розпакування…
job_ready|Встановлено
job_error|Не вдалося: {0}
retry|Повторити
plain_server_hint|Це стандартний сервер WhisperLive: введіть розмір моделі (tiny, base, small, medium, large-v3, large-v3-turbo), і сервер завантажить її першого разу. Щоб завантажувати звідси будь-які моделі, встановіть на сервер доповнення StreamRemaster.
model_name|Назва моделі
save|Зберегти
saved|Збережено
reset_position|Скинути положення субтитрів
position_reset_done|Готово: вони повернуться вниз.
section_performance|Продуктивність
performance_hint|Якщо відеокарті сервера бракує пам’яті (субтитри не надходять або з’являється попередження про пам’ять), ці два параметри звільняють чимало. Працюють лише із сервером StreamRemaster.
precision|Точність моделі
precision_auto|Автоматично
precision_int8|Заощаджувати пам’ять (int8)
precision_hint|int8 займає приблизно половину відеопам’яті й на практиці пише той самий текст.
translator_device|Перекладач працює на
device_gpu|Відеокарті
device_cpu|Процесорі (CPU)
translator_device_hint|На процесорі звільняється відеопам’ять, але перекладені субтитри надходять трохи пізніше.
interface_lang|Мова інтерфейсу
lang_auto|Як у браузері
about_text|Вихідний код доступний (ліцензія PolyForm Noncommercial). Звук іде лише на сервер, який ви тут укажете; більше нікуди нічого не надсилається.
about_based|На основі WhisperLive від Collabora.
source_code|Вихідний код
subtitle_preview|Так виглядатимуть ваші субтитри.
err_invalid_source|Це не назва моделі Hugging Face і не посилання.
err_unsupported_url|Лише посилання на Hugging Face або прямі посилання на файли .zip / .tar.gz.
err_repo_not_found|Такої моделі на Hugging Face немає (перевірте назву).
err_gated_repo|Для цієї моделі треба прийняти умови на Hugging Face; серверу потрібен HF_TOKEN.
err_not_whisper|Це не модель Whisper.
err_no_weights|У цьому репозиторії немає ваг моделі.
err_network_error|Помилка мережі. Повторіть: продовжить із того місця, де зупинилося.
err_download_failed|Завантаження не вдалося.
err_convert_failed|Не вдалося конвертувати модель.
err_bad_archive|Архів пошкоджений або небезпечний.
err_already_downloading|Уже завантажується.
err_already_installed|Уже встановлена.
err_management_disabled|Керування моделями на цьому сервері вимкнено.
err_is_default|Це типова модель сервера; видалити її звідси неможливо.
err_in_use|Її використовує поточна транскрипція.
err_not_found|Цієї моделі на сервері вже немає.
err_server_error|Помилка сервера.
err_unreachable|Не вдається зв’язатися із сервером.
err_timeout|Сервер не відповів вчасно.
err_unknown|Неочікувана помилка ({0}).
updates|Оновлення
check_updates|Перевірити оновлення
check_again|Перевірити ще раз
update_now|Оновити
update_available|Доступна версія {0} (у вас {1}).
update_latest|У вас найновіша версія ({0}).
update_rate_limited|GitHub тимчасово обмежує перевірки. Спробуйте пізніше.
update_failed|Не вдалося перевірити оновлення. Перевірте з’єднання і спробуйте ще раз.
update_how_firefox|Firefox сам встановлює нові версії. Щоб отримати її одразу, відкрийте about:addons, натисніть значок шестерні й виберіть «Перевірити наявність оновлень». Щойно випущена версія може з’явитися на сайті додатків за кілька днів.
update_how_chromium|Щоб оновити, завантажте zip для Chromium зі сторінки версії, розпакуйте його поверх старої теки й натисніть значок перезавантаження на картці StreamRemaster у chrome://extensions. Налаштування збережуться.
update_privacy|Під час перевірки в GitHub запитується лише номер найновішої версії; більше нічого не надсилається.
server_update_available|На вашому сервері версія {0}, а доступна {1}. Щоб оновити його, виконайте це на комп’ютері, де він працює:
server_version_unknown|Ваш сервер не повідомляє свою версію, отже, він старіший за цю перевірку. Щоб оновити його, виконайте це на комп’ютері, де він працює:
server_update_latest|Ваш сервер оновлений ({0}).
server_update_note|Моделі залишаються в томі Docker і не завантажуються знову. Якщо ви змінювали docker-compose.yml і git pull видає помилку, виконайте git stash перед ним і git stash pop після.
setup_or|або
use_local|Використовувати цей комп’ютер
use_local_hint|Whisper працює на відеокарті цього комп’ютера, без сервера. Модель завантажується один раз, у налаштуваннях.
local_footer|Цей комп’ютер
local_none|Моделі немає: завантажте її
local_intro|Whisper працює в браузері, на вашій відеокарті (WebGPU). Кожна модель завантажується один раз із Hugging Face і залишається в браузері. Більші моделі пишуть точніше й потребують більше відеопам’яті.
local_sizes|Завантаження {0} · займає {1} · близько {2} відеопам’яті
local_progress|Завантаження… {0} з {1}
local_cancel|Скасувати
local_gpu|Відеокарта: {0}
badge_downloaded|Завантажено
error_no_webgpu|Цей браузер не може використовувати відеокарту (WebGPU), тому не може розпізнавати мовлення на цьому комп’ютері.
error_local_missing|Спершу завантажте модель: Налаштування → Моделі на цьому комп’ютері.
error_local_failed|Розпізнавання на цьому комп’ютері зупинилося через помилку.
error_local_vram|⚠ На цьому комп’ютері замало відеопам’яті для цієї моделі. Виберіть меншу.
local_download_failed|Завантаження не вдалося ({0}).
local_confirm_delete|Видалити модель {0} з цього комп’ютера? Звільниться {1}.
local_only_english|На цьому комп’ютері субтитри можна перекладати лише англійською.
"""

LANGS['zh_CN'] = """
error_local_lost|显卡连续多次停止了转写模型。
fg_hq_badge|适合高性能显卡
where_fg_models|模型存放位置
fg_local_title|这台电脑上的流畅视频模型
fg_server_title|服务器上的流畅视频模型
fg_server_intro|服务器只负责保存：选中的模型会从服务器下载，并在这台电脑的显卡上运行。
fg_server_none|服务器上还没有流畅视频模型。
fg_server_old|此服务器不保存流畅视频模型：请将其更新到最新版本。
fg_add_server_title|添加到服务器
fg_server_loading|正在从服务器下载模型…
section_transcription|转写模型
transcription_intro|选择在哪里把语音转成文字：WhisperLive 服务器，或这台电脑的显卡。
where_transcribe|在哪里转写
engine_server|在服务器上
engine_local|在这台电脑上
trans_server_title|服务器上的转写模型
trans_local_title|这台电脑上的转写模型
badge_in_use|使用中
fg_downloaded_title|已下载
fg_add_title|添加模型
fg_add_url_placeholder|模型文件的地址（.stmodel）
fg_download_failed|无法下载（{0}）。请用浏览器下载该文件，再从这台电脑中选择它。
fg_memory|显存：1080p 视频约 {0}
fg_memory_4k|从 1080p 放大到 4K 约 {0}
fg_memory_now|正在使用的显存：约 {0}
fg_file_size|文件：{0}
fg_options|选项
fg_sharpen|锐度
fg_sharpen_off|关闭
fg_sharpen_soft|柔和
fg_sharpen_medium|中等
fg_sharpen_strong|强
fg_resolution|放大目标分辨率
fg_res_original|原始（不放大）
fg_model|流畅视频模型
fg_kind_sr|仅放大
fg_kind_fi|仅插帧
fg_builtin|内置
fg_model_none|无（不使用 AI）
section_fgmodels|流畅视频模型
fg_models_hint|流畅视频始终在这台电脑的显卡上运行。StreamRemaster 随扩展一起提供；其他模型可以放在这台电脑或你的服务器上。
fg_add_model|从这台电脑选择文件
fg_no_models|还没有下载任何模型。
fg_model_bad|该文件不是有效的模型。
tab_subs|字幕
tab_fg|流畅视频
fg_start|开启流畅视频
fg_stop|关闭流畅视频
fg_target|目标帧率
fg_target_display|与屏幕相同
fg_state_off|已关闭
fg_state_measuring|正在测量视频…
fg_state_on|{0} fps（视频 {1} fps）
fg_no_video|此页面上没有正在播放的视频。
fg_no_webgpu|此浏览器无法为此使用 GPU（WebGPU 不可用）。
fg_cannot_read|无法读取此视频：它受保护或来自其他网站。
fg_unavailable|此页面不允许使用扩展程序。
fg_auto_start|播放视频时自动开启流畅视频
subs_auto_start|播放视频时自动开始字幕
auto_start_hint|在此浏览器中，仅在您点击过扩展按钮的标签页中有效，直到该标签页转到其他网站。
fg_allow_all_sites|在所有网站上允许
extName|StreamRemaster
extDescription|为任意标签页提供实时字幕，由你自己的 Whisper 服务器转写和翻译。
start|开启字幕
stop|关闭字幕
status_idle|就绪
status_connecting|正在连接…
status_loading|正在加载模型…
status_listening|正在收听…
status_live|直播中
status_stalled|音频已停止
status_error|错误
status_noresponse|无响应
model|转写模型
model_server_default|服务器默认
model_default_tag|{0} · 默认
manage_models|管理模型
spoken_lang|音频语言
auto_detect|自动检测
detected|检测到：{0}
subs_lang|字幕语言
original_lang|不翻译
lines|行数
text_size|文字大小
save_srt|停止时保存字幕 (.srt)
advanced|高级
use_vad|跳过静音（语音检测）
settings|设置
first_load_hint|首次加载模型可能需要一分钟左右。
options_locked|关闭字幕后才能更改这些选项。
server_setup_title|连接你的服务器
server_setup_hint|StreamRemaster 可以用你电脑或网络中的 WhisperLive 服务器转写，也可以用这台电脑的显卡转写。
server_address|服务器地址
server_placeholder|例如 localhost:9090 或 192.168.1.10:9090
connect|连接
server_ok_models|已连接 · {0} 个模型
server_ok_one_model|已连接 · 1 个模型
server_plain|已连接 · 标准 WhisperLive（无模型管理）
server_checking|正在检查…
server_unreachable|无法连接服务器。它在运行吗？请检查地址和防火墙。
server_timeout|服务器未及时响应。
server_bad_url|该地址无效。
server_change|更改
server_help|如何搭建服务器？
server_help_1|你需要在一台电脑上运行 WhisperLive 服务器（免费开源），最好有 NVIDIA 显卡。小模型只用处理器也能运行。
server_help_2|然后在这里输入它的地址：电脑的 IP 和端口，例如 192.168.1.10:9090。如果就在这台电脑上，填 localhost:9090。
server_help_3|要在此页面下载和管理模型，请给服务器加装 StreamRemaster 插件。
server_help_guide|分步指南
error_capture|无法捕获此标签页（浏览器页面、扩展商店和 PDF 不允许）。
error_no_media|此页面没有视频或音频。
error_server_full|服务器繁忙。预计等待：{0} 分钟。
error_disconnected|服务器关闭了连接。
error_model_load|⚠ 服务器的显存 (VRAM) 不足以运行此模型。请选择更小的模型，或在“高级”中开启“节省内存 (int8)”。
warn_no_response|⚠ 虽然有声音，但字幕不再出现。可能是模型放不进服务器的显存 (VRAM)：请选择更小的模型，或在“高级”中开启“节省内存 (int8)”。
warn_slow_load|⚠ 模型加载时间过长。可能放不进服务器的显存 (VRAM)：请选择更小的模型，或在“高级”中开启“节省内存 (int8)”。
error_reload|请刷新页面 (F5) 后重新开始。
error_no_server|请先设置服务器。
settings_title|StreamRemaster · 设置
section_subtitles|字幕
section_interface|界面
section_about|关于
installed_models|服务器上已安装
no_models|还没有安装模型。
badge_default|默认
badge_loaded|已在内存中
badge_selected|已选择
use_model|使用
delete_model|删除
confirm_delete|从服务器删除 {0}？可释放 {1}。
add_model|添加模型
add_model_hint|粘贴 Hugging Face 上模型的名称或链接。任何 Whisper 模型都可以：faster-whisper (CTranslate2) 模型直接使用，普通 (transformers) 模型会自动转换。指向包含模型的 .zip 或 .tar.gz 的直链也可以。
add_model_placeholder|例如 Systran/faster-whisper-large-v3
download|下载
suggestions|推荐：
browse_hf|在 Hugging Face 浏览 Whisper 模型
vram_hint|模型越大越准确，但需要更多显存：small ≈ 1 GB，medium ≈ 2 GB，large ≈ 4 GB。
keep_open|下载完成前请保持此页面打开。
job_downloading|正在下载… {0} / {1}
job_downloading_nosize|正在下载… {0}
job_converting|正在转换为 faster-whisper 格式…
job_extracting|正在解压…
job_ready|已安装
job_error|失败：{0}
retry|重试
plain_server_hint|这是标准的 WhisperLive 服务器：输入模型大小（tiny、base、small、medium、large-v3、large-v3-turbo），服务器会在首次使用时下载。要从这里下载任意模型，请在服务器上安装 StreamRemaster 插件。
model_name|模型名称
save|保存
saved|已保存
reset_position|重置字幕位置
position_reset_done|完成：字幕会回到底部。
section_performance|性能
performance_hint|如果服务器显卡内存不足（字幕不出现或出现内存警告），这两个选项可以释放大量内存。仅适用于 StreamRemaster 服务器。
precision|模型精度
precision_auto|自动
precision_int8|节省内存 (int8)
precision_hint|int8 大约只用一半显存，实际写出的文字基本相同。
translator_device|翻译器运行在
device_gpu|显卡
device_cpu|处理器 (CPU)
translator_device_hint|放在处理器上可以释放显存，但翻译后的字幕会稍晚一些。
interface_lang|界面语言
lang_auto|跟随浏览器
about_text|源代码公开（PolyForm Noncommercial 许可证）。音频只会发送到你在这里设置的服务器，不会发往其他任何地方。
about_based|基于 Collabora 的 WhisperLive。
source_code|源代码
subtitle_preview|你的字幕会是这个样子。
err_invalid_source|这不是 Hugging Face 的模型名称，也不是链接。
err_unsupported_url|只支持 Hugging Face 链接或指向 .zip / .tar.gz 文件的直链。
err_repo_not_found|Hugging Face 上没有这个模型（请检查名称）。
err_gated_repo|该模型要求在 Hugging Face 上接受条款；服务器需要 HF_TOKEN。
err_not_whisper|这不是 Whisper 模型。
err_no_weights|该仓库没有模型权重。
err_network_error|网络错误。请重试：会从中断处继续。
err_download_failed|下载失败。
err_convert_failed|无法转换模型。
err_bad_archive|压缩包已损坏或不安全。
err_already_downloading|已在下载中。
err_already_installed|已经安装。
err_management_disabled|此服务器已关闭模型管理。
err_is_default|这是服务器的默认模型，不能在这里删除。
err_in_use|正在进行的转写正在使用它。
err_not_found|服务器上已没有这个模型。
err_server_error|服务器错误。
err_unreachable|无法连接服务器。
err_timeout|服务器未及时响应。
err_unknown|意外错误（{0}）。
updates|更新
check_updates|检查更新
check_again|再次检查
update_now|更新
update_available|已有 {0} 版（你的是 {1}）。
update_latest|你已是最新版本（{0}）。
update_rate_limited|GitHub 暂时限制了查询次数，请稍后再试。
update_failed|无法检查更新。请检查网络连接后重试。
update_how_firefox|Firefox 会自动安装新版本。想立即获取，请打开 about:addons，点击齿轮图标，选择“检查更新”。刚发布的版本可能要过几天才会出现在附加组件网站上。
update_how_chromium|更新方法：从版本页面下载 Chromium 版 zip，解压覆盖旧文件夹，然后在 chrome://extensions 中点击 StreamRemaster 卡片上的重新加载图标。你的设置会保留。
update_privacy|检查时只会向 GitHub 询问最新版本号，不会发送其他任何内容。
server_update_available|你的服务器是 {0} 版，已有 {1} 版。要更新，请在运行服务器的电脑上执行：
server_version_unknown|你的服务器没有报告版本，说明它比这项检查更早。要更新，请在运行服务器的电脑上执行：
server_update_latest|你的服务器已是最新（{0}）。
server_update_note|模型保留在 Docker 卷中，不会重新下载。如果你改过 docker-compose.yml 且 git pull 报错，请先执行 git stash，之后再执行 git stash pop。
setup_or|或
use_local|使用这台电脑
use_local_hint|Whisper 在这台电脑的显卡上运行，无需服务器。模型只需在设置中下载一次。
local_footer|这台电脑
local_none|还没有模型：请下载一个
local_intro|Whisper 在浏览器中用你的显卡（WebGPU）运行。每个模型只需从 Hugging Face 下载一次，并保存在浏览器中。越大的模型写得越准，也需要越多显存。
local_sizes|下载 {0} · 占用 {1} · 约 {2} 显存
local_progress|正在下载… {0} / {1}
local_cancel|取消
local_gpu|显卡：{0}
badge_downloaded|已下载
error_no_webgpu|这个浏览器无法使用显卡（WebGPU），因此无法在这台电脑上转写。
error_local_missing|请先在 设置 → 这台电脑上的模型 中下载一个模型。
error_local_failed|这台电脑上的转写因出错而停止。
error_local_vram|⚠ 这台电脑的显存不足以运行这个模型。请选择更小的模型。
local_download_failed|下载失败（{0}）。
local_confirm_delete|要从这台电脑删除 {0} 模型吗？将释放 {1}。
local_only_english|在这台电脑上，字幕只能翻译成英语。
"""

LANGS['ja'] = """
error_local_lost|グラフィックカードが文字起こしモデルを何度も続けて停止しました。
fg_hq_badge|高性能なグラフィックカード向け
where_fg_models|モデルの場所
fg_local_title|このコンピューターのなめらか動画モデル
fg_server_title|サーバーのなめらか動画モデル
fg_server_intro|サーバーは保管するだけです。選んだモデルはサーバーからダウンロードされ、このコンピューターのグラフィックカードで動きます。
fg_server_none|サーバーにはまだなめらか動画のモデルがありません。
fg_server_old|このサーバーはなめらか動画のモデルを保管できません。最新版に更新してください。
fg_add_server_title|サーバーに追加
fg_server_loading|サーバーからモデルをダウンロードしています…
section_transcription|文字起こしモデル
transcription_intro|音声をどこで文字にするかを選びます：WhisperLive サーバーか、このコンピューターのグラフィックカードです。
where_transcribe|文字起こしの場所
engine_server|サーバー
engine_local|このコンピューター
trans_server_title|サーバーの文字起こしモデル
trans_local_title|このコンピューターの文字起こしモデル
badge_in_use|使用中
fg_downloaded_title|ダウンロード済み
fg_add_title|モデルを追加
fg_add_url_placeholder|モデルファイルのアドレス（.stmodel）
fg_download_failed|ダウンロードできませんでした（{0}）。ブラウザーでファイルをダウンロードし、このコンピューターから選んでください。
fg_memory|ビデオメモリ：1080p の動画で約 {0}
fg_memory_4k|1080p から 4K へのアップスケールで約 {0}
fg_memory_now|使用中のビデオメモリ：約 {0}
fg_file_size|ファイル：{0}
fg_options|オプション
fg_sharpen|シャープネス
fg_sharpen_off|オフ
fg_sharpen_soft|弱
fg_sharpen_medium|中
fg_sharpen_strong|強
fg_resolution|アップスケール後の解像度
fg_res_original|オリジナル（アップスケールなし）
fg_model|なめらか動画のモデル
fg_kind_sr|アップスケールのみ
fg_kind_fi|中間フレームのみ
fg_builtin|内蔵
fg_model_none|なし（AI なし）
section_fgmodels|なめらか動画のモデル
fg_models_hint|なめらか動画は常にこのコンピューターのグラフィックカードで動きます。StreamRemaster は拡張機能に含まれています。ほかのモデルはこのコンピューターかサーバーに置けます。
fg_add_model|このコンピューターからファイルを選ぶ
fg_no_models|ダウンロードしたモデルはまだありません。
fg_model_bad|このファイルは有効なモデルではありません。
tab_subs|字幕
tab_fg|なめらか動画
fg_start|なめらか動画をオン
fg_stop|なめらか動画をオフ
fg_target|目標フレームレート
fg_target_display|画面に合わせる
fg_state_off|オフ
fg_state_measuring|動画を測定中…
fg_state_on|{0} fps（動画 {1} fps）
fg_no_video|このページで再生中の動画はありません。
fg_no_webgpu|このブラウザーではこの機能に GPU を使用できません（WebGPU が利用できません）。
fg_cannot_read|この動画は読み取れません。保護されているか、別のサイトのものです。
fg_unavailable|このページでは拡張機能を使用できません。
fg_auto_start|動画の再生時になめらか動画を自動でオン
subs_auto_start|動画の再生時に字幕を自動で開始
auto_start_hint|このブラウザーでは、拡張機能のボタンをクリックしたタブでのみ、別のサイトに移動するまで機能します。
fg_allow_all_sites|すべてのサイトで許可
extName|StreamRemaster
extDescription|どのタブにもリアルタイム字幕。自分の Whisper サーバーが文字起こしと翻訳をします。
start|字幕をオン
stop|字幕をオフ
status_idle|準備完了
status_connecting|接続中…
status_loading|モデルを読み込み中…
status_listening|聞き取り中…
status_live|ライブ
status_stalled|音声が止まりました
status_error|エラー
status_noresponse|応答なし
model|文字起こしモデル
model_server_default|サーバーの既定
model_default_tag|{0} · 既定
manage_models|モデルを管理
spoken_lang|音声の言語
auto_detect|自動検出
detected|検出：{0}
subs_lang|字幕の言語
original_lang|翻訳しない
lines|行数
text_size|文字サイズ
save_srt|停止時に字幕 (.srt) を保存
advanced|詳細設定
use_vad|無音をスキップ（音声検出）
settings|設定
first_load_hint|モデルの初回読み込みには最大 1 分ほどかかることがあります。
options_locked|これらの設定を変えるには字幕をオフにしてください。
server_setup_title|サーバーに接続
server_setup_hint|StreamRemaster は、パソコンかネットワーク上の WhisperLive サーバー、またはこのコンピューターのグラフィックカードで文字起こしします。
server_address|サーバーのアドレス
server_placeholder|例：localhost:9090 または 192.168.1.10:9090
connect|接続
server_ok_models|接続済み · モデル {0} 個
server_ok_one_model|接続済み · モデル 1 個
server_plain|接続済み · 標準の WhisperLive（モデル管理なし）
server_checking|確認中…
server_unreachable|サーバーに接続できません。起動していますか？アドレスとファイアウォールを確認してください。
server_timeout|サーバーが時間内に応答しませんでした。
server_bad_url|このアドレスは無効です。
server_change|変更
server_help|サーバーの用意のしかた
server_help_1|パソコンで WhisperLive サーバー（無料のオープンソース）を動かします。NVIDIA のグラフィックボードがあると理想的です。小さなモデルは CPU だけでも動きます。
server_help_2|次にここにアドレスを入力します：パソコンの IP とポート、例 192.168.1.10:9090。同じパソコンで動かすなら localhost:9090。
server_help_3|このページからモデルをダウンロード・管理するには、サーバーに StreamRemaster のアドオンを追加してください。
server_help_guide|手順ガイド
error_capture|このタブはキャプチャできません（ブラウザーのページ、拡張機能ストア、PDF は対象外です）。
error_no_media|このページには動画も音声もありません。
error_server_full|サーバーが混雑しています。待ち時間の目安：{0} 分。
error_disconnected|サーバーが接続を閉じました。
error_model_load|⚠ このモデルにはサーバーのビデオメモリ (VRAM) が足りません。小さいモデルを選ぶか、詳細設定で「メモリを節約 (int8)」をオンにしてください。
warn_no_response|⚠ 音が出ているのに字幕が届かなくなりました。モデルがサーバーのビデオメモリ (VRAM) に収まっていないようです。小さいモデルを選ぶか、詳細設定で「メモリを節約 (int8)」をオンにしてください。
warn_slow_load|⚠ モデルの読み込みに時間がかかりすぎています。サーバーのビデオメモリ (VRAM) に収まらないのかもしれません。小さいモデルを選ぶか、詳細設定で「メモリを節約 (int8)」をオンにしてください。
error_reload|ページを再読み込み (F5) して、もう一度始めてください。
error_no_server|先にサーバーを設定してください。
settings_title|StreamRemaster · 設定
section_subtitles|字幕
section_interface|インターフェース
section_about|このアプリについて
installed_models|サーバーにインストール済み
no_models|まだモデルがありません。
badge_default|既定
badge_loaded|メモリ上
badge_selected|選択中
use_model|使う
delete_model|削除
confirm_delete|{0} をサーバーから削除しますか？ {1} が空きます。
add_model|モデルを追加
add_model_hint|Hugging Face のモデル名かリンクを貼り付けてください。Whisper モデルなら何でも使えます。faster-whisper (CTranslate2) のモデルはそのまま、通常の (transformers) モデルは自動で変換されます。モデル入りの .zip や .tar.gz への直接リンクも使えます。
add_model_placeholder|例：Systran/faster-whisper-large-v3
download|ダウンロード
suggestions|おすすめ：
browse_hf|Hugging Face で Whisper モデルを見る
vram_hint|大きいモデルほど正確ですが、ビデオメモリを多く使います：small ≈ 1 GB、medium ≈ 2 GB、large ≈ 4 GB。
keep_open|ダウンロードが終わるまでこのページを開いたままにしてください。
job_downloading|ダウンロード中… {0} / {1}
job_downloading_nosize|ダウンロード中… {0}
job_converting|faster-whisper 形式に変換中…
job_extracting|展開中…
job_ready|インストール済み
job_error|失敗：{0}
retry|再試行
plain_server_hint|標準の WhisperLive サーバーです。モデルのサイズ（tiny、base、small、medium、large-v3、large-v3-turbo）を入力すると、初回にサーバーがダウンロードします。ここから任意のモデルをダウンロードするには、サーバーに StreamRemaster のアドオンを入れてください。
model_name|モデル名
save|保存
saved|保存しました
reset_position|字幕の位置をリセット
position_reset_done|完了：下に戻ります。
section_performance|パフォーマンス
performance_hint|サーバーのグラフィックボードのメモリが足りないとき（字幕が届かない、メモリの警告が出る）、この 2 つの設定で大きく空けられます。StreamRemaster のサーバーでのみ有効です。
precision|モデルの精度
precision_auto|自動
precision_int8|メモリを節約 (int8)
precision_hint|int8 はビデオメモリを約半分しか使わず、実際にはほぼ同じ文字を書き出します。
translator_device|翻訳を実行する場所
device_gpu|GPU
device_cpu|CPU
translator_device_hint|CPU で動かすとビデオメモリが空きますが、翻訳字幕は少し遅れて届きます。
interface_lang|表示言語
lang_auto|ブラウザーに合わせる
about_text|ソースコード公開（PolyForm Noncommercial ライセンス）。音声はここで設定したサーバーにだけ送られ、ほかには一切送られません。
about_based|Collabora の WhisperLive をもとにしています。
source_code|ソースコード
subtitle_preview|字幕はこのように表示されます。
err_invalid_source|Hugging Face のモデル名でもリンクでもありません。
err_unsupported_url|Hugging Face のリンクか、.zip / .tar.gz ファイルへの直接リンクのみです。
err_repo_not_found|そのモデルは Hugging Face にありません（名前を確認してください）。
err_gated_repo|そのモデルは Hugging Face で利用条件への同意が必要です。サーバーに HF_TOKEN が必要です。
err_not_whisper|Whisper モデルではありません。
err_no_weights|そのリポジトリにはモデルの重みがありません。
err_network_error|ネットワークエラー。再試行すると、止まったところから続きます。
err_download_failed|ダウンロードに失敗しました。
err_convert_failed|モデルを変換できませんでした。
err_bad_archive|アーカイブが壊れているか、安全ではありません。
err_already_downloading|すでにダウンロード中です。
err_already_installed|すでにインストールされています。
err_management_disabled|このサーバーではモデル管理が無効です。
err_is_default|サーバーの既定のモデルなので、ここからは削除できません。
err_in_use|実行中の文字起こしが使用しています。
err_not_found|そのモデルはもうサーバーにありません。
err_server_error|サーバーエラー。
err_unreachable|サーバーに接続できません。
err_timeout|サーバーが時間内に応答しませんでした。
err_unknown|予期しないエラー（{0}）。
updates|アップデート
check_updates|アップデートを確認
check_again|もう一度確認
update_now|アップデート
update_available|バージョン {0} が出ています（現在は {1}）。
update_latest|最新バージョンです（{0}）。
update_rate_limited|GitHub がしばらく確認を制限しています。後でもう一度お試しください。
update_failed|アップデートを確認できませんでした。接続を確認してもう一度お試しください。
update_how_firefox|Firefox は新しいバージョンを自動でインストールします。すぐに入れるには about:addons を開き、歯車アイコンから「今すぐ更新を確認」を選んでください。出たばかりのバージョンはアドオンサイトに載るまで数日かかることがあります。
update_how_chromium|アップデートするには、バージョンのページから Chromium 用の zip をダウンロードして古いフォルダーに上書きで展開し、chrome://extensions の StreamRemaster のカードで再読み込みアイコンを押してください。設定はそのまま残ります。
update_privacy|確認では GitHub に最新バージョンの番号を問い合わせるだけで、ほかには何も送信しません。
server_update_available|サーバーはバージョン {0} で、{1} が出ています。アップデートするには、サーバーが動いているパソコンで次を実行してください：
server_version_unknown|サーバーがバージョンを伝えていないため、この確認機能より古いものです。アップデートするには、サーバーが動いているパソコンで次を実行してください：
server_update_latest|サーバーは最新です（{0}）。
server_update_note|モデルは Docker ボリュームに残り、再ダウンロードされません。docker-compose.yml を変更していて git pull がエラーになる場合は、先に git stash を、後で git stash pop を実行してください。
setup_or|または
use_local|このコンピューターを使う
use_local_hint|Whisper はこのコンピューターのグラフィックカードで動き、サーバーは不要です。モデルは設定で一度だけダウンロードします。
local_footer|このコンピューター
local_none|モデルがありません：ダウンロードしてください
local_intro|Whisper はブラウザー内で、あなたのグラフィックカード（WebGPU）を使って動きます。各モデルは Hugging Face から一度だけダウンロードされ、ブラウザーに保存されます。大きいモデルほど正確ですが、より多くのビデオメモリが必要です。
local_sizes|ダウンロード {0} · 容量 {1} · ビデオメモリ約 {2}
local_progress|ダウンロード中… {0} / {1}
local_cancel|キャンセル
local_gpu|グラフィックカード：{0}
badge_downloaded|ダウンロード済み
error_no_webgpu|このブラウザーはグラフィックカード（WebGPU）を使えないため、このコンピューターでは文字起こしできません。
error_local_missing|まず 設定 → このコンピューターのモデル でモデルをダウンロードしてください。
error_local_failed|このコンピューターでの文字起こしがエラーで停止しました。
error_local_vram|⚠ このコンピューターにはこのモデルに必要なビデオメモリが足りません。小さいモデルを選んでください。
local_download_failed|ダウンロードに失敗しました（{0}）。
local_confirm_delete|このコンピューターから {0} モデルを削除しますか？ {1} が空きます。
local_only_english|このコンピューターでは、字幕は英語にのみ翻訳できます。
"""

LANGS['ko'] = """
error_local_lost|그래픽 카드가 받아쓰기 모델을 여러 번 연속으로 멈췄습니다.
fg_hq_badge|고성능 그래픽 카드용
where_fg_models|모델 위치
fg_local_title|이 컴퓨터의 부드러운 영상 모델
fg_server_title|서버의 부드러운 영상 모델
fg_server_intro|서버는 모델을 보관만 합니다. 선택한 모델은 서버에서 내려받아 이 컴퓨터의 그래픽 카드에서 실행됩니다.
fg_server_none|서버에 아직 부드러운 영상 모델이 없습니다.
fg_server_old|이 서버는 부드러운 영상 모델을 보관하지 않습니다. 최신 버전으로 업데이트하세요.
fg_add_server_title|서버에 추가
fg_server_loading|서버에서 모델을 내려받는 중…
section_transcription|받아쓰기 모델
transcription_intro|음성을 어디에서 글자로 바꿀지 고르세요: WhisperLive 서버 또는 이 컴퓨터의 그래픽 카드.
where_transcribe|받아쓰기 위치
engine_server|서버에서
engine_local|이 컴퓨터에서
trans_server_title|서버의 받아쓰기 모델
trans_local_title|이 컴퓨터의 받아쓰기 모델
badge_in_use|사용 중
fg_downloaded_title|다운로드한 모델
fg_add_title|모델 추가
fg_add_url_placeholder|모델 파일 주소(.stmodel)
fg_download_failed|다운로드하지 못했습니다({0}). 브라우저로 파일을 받은 뒤 이 컴퓨터에서 선택하세요.
fg_memory|그래픽 메모리: 1080p 영상에서 약 {0}
fg_memory_4k|1080p를 4K로 업스케일하면 약 {0}
fg_memory_now|사용 중인 그래픽 메모리: 약 {0}
fg_file_size|파일: {0}
fg_options|옵션
fg_sharpen|선명도
fg_sharpen_off|끄기
fg_sharpen_soft|약하게
fg_sharpen_medium|보통
fg_sharpen_strong|강하게
fg_resolution|업스케일 목표 해상도
fg_res_original|원본 (업스케일 없음)
fg_model|부드러운 영상 모델
fg_kind_sr|업스케일만
fg_kind_fi|중간 프레임만
fg_builtin|기본 제공
fg_model_none|없음(AI 사용 안 함)
section_fgmodels|부드러운 영상 모델
fg_models_hint|부드러운 영상은 항상 이 컴퓨터의 그래픽 카드에서 실행됩니다. StreamRemaster는 확장 프로그램에 포함되어 있으며, 다른 모델은 이 컴퓨터나 서버에 둘 수 있습니다.
fg_add_model|이 컴퓨터에서 파일 선택
fg_no_models|아직 다운로드한 모델이 없습니다.
fg_model_bad|유효한 모델 파일이 아닙니다.
tab_subs|자막
tab_fg|부드러운 영상
fg_start|부드러운 영상 켜기
fg_stop|부드러운 영상 끄기
fg_target|목표 프레임 속도
fg_target_display|화면에 맞춤
fg_state_off|꺼짐
fg_state_measuring|영상 측정 중…
fg_state_on|{0} fps (영상 {1} fps)
fg_no_video|이 페이지에서 재생 중인 영상이 없습니다.
fg_no_webgpu|이 브라우저는 이 기능에 GPU를 사용할 수 없습니다(WebGPU를 사용할 수 없음).
fg_cannot_read|이 영상은 읽을 수 없습니다. 보호되어 있거나 다른 사이트에서 제공됩니다.
fg_unavailable|이 페이지는 확장 프로그램을 허용하지 않습니다.
fg_auto_start|동영상이 재생되면 부드러운 영상 자동으로 켜기
subs_auto_start|동영상이 재생되면 자막 자동으로 시작
auto_start_hint|이 브라우저에서는 확장 프로그램 버튼을 클릭한 탭에서만, 다른 사이트로 이동하기 전까지 작동합니다.
fg_allow_all_sites|모든 사이트에서 허용
extName|StreamRemaster
extDescription|어떤 탭에서든 실시간 자막. 내 Whisper 서버가 받아쓰고 번역합니다.
start|자막 켜기
stop|자막 끄기
status_idle|준비됨
status_connecting|연결 중…
status_loading|모델 불러오는 중…
status_listening|듣는 중…
status_live|실시간
status_stalled|오디오 멈춤
status_error|오류
status_noresponse|응답 없음
model|받아쓰기 모델
model_server_default|서버 기본값
model_default_tag|{0} · 기본
manage_models|모델 관리
spoken_lang|오디오 언어
auto_detect|자동 감지
detected|감지됨: {0}
subs_lang|자막 언어
original_lang|번역 안 함
lines|줄 수
text_size|글자 크기
save_srt|끌 때 자막(.srt) 저장
advanced|고급
use_vad|무음 건너뛰기(음성 감지)
settings|설정
first_load_hint|모델을 처음 불러올 때는 최대 1분 정도 걸릴 수 있습니다.
options_locked|이 설정을 바꾸려면 자막을 끄세요.
server_setup_title|서버 연결
server_setup_hint|StreamRemaster는 컴퓨터나 네트워크의 WhisperLive 서버, 또는 이 컴퓨터의 그래픽 카드로 받아씁니다.
server_address|서버 주소
server_placeholder|예: localhost:9090 또는 192.168.1.10:9090
connect|연결
server_ok_models|연결됨 · 모델 {0}개
server_ok_one_model|연결됨 · 모델 1개
server_plain|연결됨 · 표준 WhisperLive(모델 관리 없음)
server_checking|확인 중…
server_unreachable|서버에 연결할 수 없습니다. 켜져 있나요? 주소와 방화벽을 확인하세요.
server_timeout|서버가 제때 응답하지 않았습니다.
server_bad_url|올바른 주소가 아닙니다.
server_change|변경
server_help|서버는 어떻게 준비하나요?
server_help_1|컴퓨터에서 WhisperLive 서버(무료 오픈 소스)를 실행해야 합니다. NVIDIA 그래픽 카드가 있으면 가장 좋습니다. 작은 모델은 프로세서만으로도 돌아갑니다.
server_help_2|그런 다음 여기에 주소를 입력하세요: 컴퓨터 IP와 포트, 예 192.168.1.10:9090. 같은 컴퓨터라면 localhost:9090.
server_help_3|이 페이지에서 모델을 내려받고 관리하려면 서버에 StreamRemaster 애드온을 추가하세요.
server_help_guide|단계별 안내
error_capture|이 탭은 캡처할 수 없습니다(브라우저 페이지, 확장 프로그램 스토어, PDF는 제외).
error_no_media|이 페이지에는 동영상이나 오디오가 없습니다.
error_server_full|서버가 바쁩니다. 예상 대기: {0}분.
error_disconnected|서버가 연결을 닫았습니다.
error_model_load|⚠ 서버의 그래픽 메모리(VRAM)가 이 모델에 부족합니다. 더 작은 모델을 고르거나 고급에서 ‘메모리 절약(int8)’을 켜세요.
warn_no_response|⚠ 소리가 나는데도 자막이 오지 않습니다. 모델이 서버의 그래픽 메모리(VRAM)에 들어가지 않는 것 같습니다. 더 작은 모델을 고르거나 고급에서 ‘메모리 절약(int8)’을 켜세요.
warn_slow_load|⚠ 모델을 불러오는 데 너무 오래 걸립니다. 서버의 그래픽 메모리(VRAM)에 들어가지 않을 수 있습니다. 더 작은 모델을 고르거나 고급에서 ‘메모리 절약(int8)’을 켜세요.
error_reload|페이지를 새로 고침(F5)하고 다시 시작하세요.
error_no_server|먼저 서버를 설정하세요.
settings_title|StreamRemaster · 설정
section_subtitles|자막
section_interface|인터페이스
section_about|정보
installed_models|서버에 설치됨
no_models|아직 설치된 모델이 없습니다.
badge_default|기본
badge_loaded|메모리에 있음
badge_selected|선택됨
use_model|사용
delete_model|삭제
confirm_delete|서버에서 {0}을(를) 삭제할까요? {1}이(가) 확보됩니다.
add_model|모델 추가
add_model_hint|Hugging Face 모델의 이름이나 링크를 붙여 넣으세요. 어떤 Whisper 모델이든 됩니다. faster-whisper(CTranslate2) 모델은 그대로 쓰고, 일반(transformers) 모델은 자동으로 변환합니다. 모델이 든 .zip이나 .tar.gz 직접 링크도 됩니다.
add_model_placeholder|예: Systran/faster-whisper-large-v3
download|내려받기
suggestions|추천:
browse_hf|Hugging Face에서 Whisper 모델 보기
vram_hint|큰 모델일수록 정확하지만 그래픽 메모리를 더 씁니다: small ≈ 1 GB, medium ≈ 2 GB, large ≈ 4 GB.
keep_open|내려받기가 끝날 때까지 이 페이지를 열어 두세요.
job_downloading|내려받는 중… {0} / {1}
job_downloading_nosize|내려받는 중… {0}
job_converting|faster-whisper 형식으로 변환 중…
job_extracting|압축 푸는 중…
job_ready|설치됨
job_error|실패: {0}
retry|다시 시도
plain_server_hint|표준 WhisperLive 서버입니다. 모델 크기(tiny, base, small, medium, large-v3, large-v3-turbo)를 입력하면 서버가 처음에 내려받습니다. 여기서 아무 모델이나 내려받으려면 서버에 StreamRemaster 애드온을 설치하세요.
model_name|모델 이름
save|저장
saved|저장됨
reset_position|자막 위치 초기화
position_reset_done|완료: 다시 아래로 갑니다.
section_performance|성능
performance_hint|서버 그래픽 카드의 메모리가 모자라면(자막이 오지 않거나 메모리 경고가 뜨면) 이 두 옵션으로 꽤 많이 확보할 수 있습니다. StreamRemaster 서버에서만 작동합니다.
precision|모델 정밀도
precision_auto|자동
precision_int8|메모리 절약(int8)
precision_hint|int8은 그래픽 메모리를 절반쯤만 쓰며, 실제로는 같은 글을 씁니다.
translator_device|번역기 실행 위치
device_gpu|그래픽 카드
device_cpu|프로세서(CPU)
translator_device_hint|프로세서에서 돌리면 그래픽 메모리가 확보되지만 번역 자막이 조금 늦게 옵니다.
interface_lang|인터페이스 언어
lang_auto|브라우저와 같게
about_text|소스 코드 공개(PolyForm Noncommercial 라이선스). 오디오는 여기서 설정한 서버로만 가며, 다른 곳으로는 아무것도 보내지 않습니다.
about_based|Collabora의 WhisperLive를 바탕으로 합니다.
source_code|소스 코드
subtitle_preview|자막은 이렇게 보입니다.
err_invalid_source|Hugging Face 모델 이름도 링크도 아닙니다.
err_unsupported_url|Hugging Face 링크나 .zip / .tar.gz 파일 직접 링크만 됩니다.
err_repo_not_found|그런 모델이 Hugging Face에 없습니다(이름을 확인하세요).
err_gated_repo|이 모델은 Hugging Face에서 이용 조건에 동의해야 합니다. 서버에 HF_TOKEN이 필요합니다.
err_not_whisper|Whisper 모델이 아닙니다.
err_no_weights|이 저장소에는 모델 가중치가 없습니다.
err_network_error|네트워크 오류입니다. 다시 시도하면 멈춘 곳부터 이어집니다.
err_download_failed|내려받기에 실패했습니다.
err_convert_failed|모델을 변환하지 못했습니다.
err_bad_archive|압축 파일이 손상되었거나 안전하지 않습니다.
err_already_downloading|이미 내려받는 중입니다.
err_already_installed|이미 설치되어 있습니다.
err_management_disabled|이 서버에서는 모델 관리가 꺼져 있습니다.
err_is_default|서버의 기본 모델이라 여기서 삭제할 수 없습니다.
err_in_use|진행 중인 받아쓰기가 사용하고 있습니다.
err_not_found|그 모델은 더 이상 서버에 없습니다.
err_server_error|서버 오류.
err_unreachable|서버에 연결할 수 없습니다.
err_timeout|서버가 제때 응답하지 않았습니다.
err_unknown|예상치 못한 오류({0}).
updates|업데이트
check_updates|업데이트 확인
check_again|다시 확인
update_now|업데이트
update_available|{0} 버전이 나왔습니다 (현재 {1}).
update_latest|최신 버전입니다 ({0}).
update_rate_limited|GitHub가 잠시 확인 횟수를 제한하고 있습니다. 나중에 다시 시도하세요.
update_failed|업데이트를 확인하지 못했습니다. 연결을 확인하고 다시 시도하세요.
update_how_firefox|Firefox는 새 버전을 자동으로 설치합니다. 지금 바로 받으려면 about:addons를 열고 톱니바퀴 아이콘을 누른 뒤 ‘업데이트 확인’을 선택하세요. 갓 나온 버전은 부가 기능 사이트에 올라오기까지 며칠 걸릴 수 있습니다.
update_how_chromium|업데이트하려면 버전 페이지에서 Chromium용 zip을 내려받아 기존 폴더에 덮어써서 압축을 풀고, chrome://extensions의 StreamRemaster 카드에서 새로고침 아이콘을 누르세요. 설정은 그대로 유지됩니다.
update_privacy|확인할 때는 GitHub에 최신 버전 번호만 물어보며, 그 밖에는 아무것도 보내지 않습니다.
server_update_available|서버는 {0} 버전이고 {1} 버전이 나왔습니다. 업데이트하려면 서버가 실행 중인 컴퓨터에서 다음을 실행하세요:
server_version_unknown|서버가 버전을 알려 주지 않으므로 이 확인 기능보다 오래된 버전입니다. 업데이트하려면 서버가 실행 중인 컴퓨터에서 다음을 실행하세요:
server_update_latest|서버가 최신 상태입니다 ({0}).
server_update_note|모델은 Docker 볼륨에 남아 있어 다시 내려받지 않습니다. docker-compose.yml을 수정했고 git pull이 오류를 내면 먼저 git stash를, 끝난 뒤 git stash pop을 실행하세요.
setup_or|또는
use_local|이 컴퓨터 사용
use_local_hint|Whisper가 서버 없이 이 컴퓨터의 그래픽 카드에서 실행됩니다. 모델은 설정에서 한 번만 내려받으면 됩니다.
local_footer|이 컴퓨터
local_none|모델 없음: 하나 내려받으세요
local_intro|Whisper가 브라우저에서 그래픽 카드(WebGPU)로 실행됩니다. 각 모델은 Hugging Face에서 한 번만 내려받아 브라우저에 보관됩니다. 큰 모델일수록 더 정확하지만 그래픽 메모리가 더 필요합니다.
local_sizes|다운로드 {0} · 용량 {1} · 그래픽 메모리 약 {2}
local_progress|다운로드 중… {0} / {1}
local_cancel|취소
local_gpu|그래픽 카드: {0}
badge_downloaded|다운로드됨
error_no_webgpu|이 브라우저는 그래픽 카드(WebGPU)를 사용할 수 없어 이 컴퓨터에서 받아쓸 수 없습니다.
error_local_missing|먼저 설정 → 이 컴퓨터의 모델에서 모델을 내려받으세요.
error_local_failed|이 컴퓨터에서의 받아쓰기가 오류로 멈췄습니다.
error_local_vram|⚠ 이 컴퓨터의 그래픽 메모리가 이 모델에 부족합니다. 더 작은 모델을 고르세요.
local_download_failed|다운로드에 실패했습니다 ({0}).
local_confirm_delete|이 컴퓨터에서 {0} 모델을 삭제할까요? {1}가 확보됩니다.
local_only_english|이 컴퓨터에서는 자막을 영어로만 번역할 수 있습니다.
"""

LANGS['th'] = """
error_local_lost|การ์ดจอหยุดโมเดลถอดเสียงหลายครั้งติดต่อกัน
fg_hq_badge|สำหรับการ์ดจอประสิทธิภาพสูง
where_fg_models|โมเดลอยู่ที่ไหน
fg_local_title|โมเดลวิดีโอลื่นไหลบนคอมพิวเตอร์เครื่องนี้
fg_server_title|โมเดลวิดีโอลื่นไหลบนเซิร์ฟเวอร์
fg_server_intro|เซิร์ฟเวอร์มีหน้าที่เก็บไว้เท่านั้น โมเดลที่เลือกจะถูกดาวน์โหลดจากเซิร์ฟเวอร์และทำงานบนการ์ดจอของคอมพิวเตอร์เครื่องนี้
fg_server_none|เซิร์ฟเวอร์ยังไม่มีโมเดลวิดีโอลื่นไหล
fg_server_old|เซิร์ฟเวอร์นี้ไม่เก็บโมเดลวิดีโอลื่นไหล โปรดอัปเดตเป็นเวอร์ชันล่าสุด
fg_add_server_title|เพิ่มลงในเซิร์ฟเวอร์
fg_server_loading|กำลังดาวน์โหลดโมเดลจากเซิร์ฟเวอร์…
section_transcription|โมเดลถอดเสียง
transcription_intro|เลือกว่าจะแปลงเสียงพูดเป็นข้อความที่ไหน: บนเซิร์ฟเวอร์ WhisperLive หรือบนการ์ดจอของคอมพิวเตอร์เครื่องนี้
where_transcribe|ถอดเสียงที่ไหน
engine_server|บนเซิร์ฟเวอร์
engine_local|บนคอมพิวเตอร์เครื่องนี้
trans_server_title|โมเดลถอดเสียงบนเซิร์ฟเวอร์
trans_local_title|โมเดลถอดเสียงบนคอมพิวเตอร์เครื่องนี้
badge_in_use|กำลังใช้
fg_downloaded_title|ที่ดาวน์โหลดแล้ว
fg_add_title|เพิ่มโมเดล
fg_add_url_placeholder|ที่อยู่ของไฟล์โมเดล (.stmodel)
fg_download_failed|ดาวน์โหลดไม่ได้ ({0}) ดาวน์โหลดไฟล์ด้วยเบราว์เซอร์แล้วเลือกจากคอมพิวเตอร์เครื่องนี้
fg_memory|หน่วยความจำการ์ดจอ: ประมาณ {0} กับวิดีโอ 1080p
fg_memory_4k|ประมาณ {0} เมื่อขยายภาพจาก 1080p เป็น 4K
fg_memory_now|หน่วยความจำการ์ดจอที่ใช้อยู่: ประมาณ {0}
fg_file_size|ไฟล์: {0}
fg_options|ตัวเลือก
fg_sharpen|ความคมชัด
fg_sharpen_off|ปิด
fg_sharpen_soft|เบา
fg_sharpen_medium|ปานกลาง
fg_sharpen_strong|แรง
fg_resolution|ความละเอียดเป้าหมายของการขยายภาพ
fg_res_original|ต้นฉบับ (ไม่ขยายภาพ)
fg_model|โมเดลวิดีโอลื่นไหล
fg_kind_sr|ขยายภาพเท่านั้น
fg_kind_fi|เฟรมแทรกเท่านั้น
fg_builtin|ในตัว
fg_model_none|ไม่มี (ไม่ใช้ AI)
section_fgmodels|โมเดลวิดีโอลื่นไหล
fg_models_hint|วิดีโอลื่นไหลทำงานบนการ์ดจอของคอมพิวเตอร์เครื่องนี้เสมอ StreamRemaster มาพร้อมส่วนขยาย ส่วนโมเดลอื่นเก็บไว้ในคอมพิวเตอร์เครื่องนี้หรือบนเซิร์ฟเวอร์ของคุณก็ได้
fg_add_model|เลือกไฟล์จากคอมพิวเตอร์เครื่องนี้
fg_no_models|ยังไม่มีโมเดลที่ดาวน์โหลด
fg_model_bad|ไฟล์นี้ไม่ใช่โมเดลที่ถูกต้อง
tab_subs|คำบรรยาย
tab_fg|วิดีโอลื่นไหล
fg_start|เปิดวิดีโอลื่นไหล
fg_stop|ปิดวิดีโอลื่นไหล
fg_target|อัตราเฟรมเป้าหมาย
fg_target_display|เท่ากับหน้าจอ
fg_state_off|ปิด
fg_state_measuring|กำลังวัดวิดีโอ…
fg_state_on|{0} fps (วิดีโอ {1} fps)
fg_no_video|ไม่มีวิดีโอที่กำลังเล่นในหน้านี้
fg_no_webgpu|เบราว์เซอร์นี้ใช้ GPU สำหรับงานนี้ไม่ได้ (ไม่มี WebGPU)
fg_cannot_read|อ่านวิดีโอนี้ไม่ได้: วิดีโอได้รับการป้องกันหรือมาจากเว็บไซต์อื่น
fg_unavailable|หน้านี้ไม่อนุญาตให้ใช้ส่วนขยาย
fg_auto_start|เปิดวิดีโอลื่นไหลอัตโนมัติเมื่อเล่นวิดีโอ
subs_auto_start|เริ่มคำบรรยายอัตโนมัติเมื่อเล่นวิดีโอ
auto_start_hint|ในเบราว์เซอร์นี้ ใช้ได้เฉพาะในแท็บที่คุณคลิกปุ่มของส่วนขยายแล้ว จนกว่าแท็บนั้นจะไปยังเว็บไซต์อื่น
fg_allow_all_sites|อนุญาตในทุกเว็บไซต์
extName|StreamRemaster
extDescription|คำบรรยายสดสำหรับทุกแท็บ ถอดความและแปลโดยเซิร์ฟเวอร์ Whisper ของคุณเอง
start|เปิดคำบรรยาย
stop|ปิดคำบรรยาย
status_idle|พร้อม
status_connecting|กำลังเชื่อมต่อ…
status_loading|กำลังโหลดโมเดล…
status_listening|กำลังฟัง…
status_live|สด
status_stalled|เสียงหยุดแล้ว
status_error|ข้อผิดพลาด
status_noresponse|ไม่มีการตอบกลับ
model|โมเดลถอดเสียง
model_server_default|ค่าเริ่มต้นของเซิร์ฟเวอร์
model_default_tag|{0} · ค่าเริ่มต้น
manage_models|จัดการโมเดล
spoken_lang|ภาษาของเสียง
auto_detect|ตรวจหาอัตโนมัติ
detected|ตรวจพบ: {0}
subs_lang|คำบรรยายเป็นภาษา
original_lang|ไม่แปล
lines|จำนวนบรรทัด
text_size|ขนาดตัวอักษร
save_srt|บันทึกคำบรรยาย (.srt) เมื่อหยุด
advanced|ขั้นสูง
use_vad|ข้ามช่วงเงียบ (ตรวจจับเสียงพูด)
settings|การตั้งค่า
first_load_hint|การโหลดโมเดลครั้งแรกอาจใช้เวลาถึงหนึ่งนาที
options_locked|ปิดคำบรรยายก่อนจึงจะเปลี่ยนตัวเลือกเหล่านี้ได้
server_setup_title|เชื่อมต่อเซิร์ฟเวอร์ของคุณ
server_setup_hint|StreamRemaster ถอดเสียงด้วยเซิร์ฟเวอร์ WhisperLive บนคอมพิวเตอร์หรือในเครือข่ายของคุณ หรือด้วยการ์ดจอของคอมพิวเตอร์เครื่องนี้
server_address|ที่อยู่เซิร์ฟเวอร์
server_placeholder|เช่น localhost:9090 หรือ 192.168.1.10:9090
connect|เชื่อมต่อ
server_ok_models|เชื่อมต่อแล้ว · {0} โมเดล
server_ok_one_model|เชื่อมต่อแล้ว · 1 โมเดล
server_plain|เชื่อมต่อแล้ว · WhisperLive มาตรฐาน (ไม่มีการจัดการโมเดล)
server_checking|กำลังตรวจสอบ…
server_unreachable|ติดต่อเซิร์ฟเวอร์ไม่ได้ เปิดอยู่หรือไม่ ตรวจสอบที่อยู่และไฟร์วอลล์
server_timeout|เซิร์ฟเวอร์ไม่ตอบกลับทันเวลา
server_bad_url|ที่อยู่นี้ไม่ถูกต้อง
server_change|เปลี่ยน
server_help|จะตั้งเซิร์ฟเวอร์อย่างไร
server_help_1|คุณต้องมีเซิร์ฟเวอร์ WhisperLive (ฟรีและโอเพนซอร์ส) บนคอมพิวเตอร์ ถ้ามีการ์ดจอ NVIDIA จะดีที่สุด โมเดลเล็กใช้แค่ซีพียูก็ได้
server_help_2|จากนั้นพิมพ์ที่อยู่ของมันที่นี่: IP ของคอมพิวเตอร์และพอร์ต เช่น 192.168.1.10:9090 ถ้าอยู่บนคอมพิวเตอร์เครื่องนี้ ให้ใช้ localhost:9090
server_help_3|หากต้องการดาวน์โหลดและจัดการโมเดลจากหน้านี้ ให้ติดตั้งส่วนเสริม StreamRemaster บนเซิร์ฟเวอร์
server_help_guide|คู่มือทีละขั้นตอน
error_capture|จับภาพแท็บนี้ไม่ได้ (หน้าของเบราว์เซอร์ ร้านส่วนขยาย และ PDF ใช้ไม่ได้)
error_no_media|หน้านี้ไม่มีวิดีโอหรือเสียง
error_server_full|เซิร์ฟเวอร์ไม่ว่าง เวลารอโดยประมาณ: {0} นาที
error_disconnected|เซิร์ฟเวอร์ปิดการเชื่อมต่อแล้ว
error_model_load|⚠ หน่วยความจำกราฟิก (VRAM) ของเซิร์ฟเวอร์ไม่พอสำหรับโมเดลนี้ เลือกโมเดลที่เล็กลง หรือเปิด “ประหยัดหน่วยความจำ (int8)” ในขั้นสูง
warn_no_response|⚠ คำบรรยายหยุดมาทั้งที่มีเสียง โมเดลอาจใส่ไม่พอในหน่วยความจำกราฟิก (VRAM) ของเซิร์ฟเวอร์ เลือกโมเดลที่เล็กลง หรือเปิด “ประหยัดหน่วยความจำ (int8)” ในขั้นสูง
warn_slow_load|⚠ โมเดลโหลดนานเกินไป อาจใส่ไม่พอในหน่วยความจำกราฟิก (VRAM) ของเซิร์ฟเวอร์ เลือกโมเดลที่เล็กลง หรือเปิด “ประหยัดหน่วยความจำ (int8)” ในขั้นสูง
error_reload|โหลดหน้าใหม่ (F5) แล้วเริ่มอีกครั้ง
error_no_server|ตั้งค่าเซิร์ฟเวอร์ก่อน
settings_title|StreamRemaster · การตั้งค่า
section_subtitles|คำบรรยาย
section_interface|หน้าตาโปรแกรม
section_about|เกี่ยวกับ
installed_models|ติดตั้งบนเซิร์ฟเวอร์แล้ว
no_models|ยังไม่มีโมเดลที่ติดตั้ง
badge_default|ค่าเริ่มต้น
badge_loaded|อยู่ในหน่วยความจำ
badge_selected|เลือกแล้ว
use_model|ใช้
delete_model|ลบ
confirm_delete|ลบ {0} ออกจากเซิร์ฟเวอร์ไหม จะได้พื้นที่คืน {1}
add_model|เพิ่มโมเดล
add_model_hint|วางชื่อหรือลิงก์ของโมเดลจาก Hugging Face ใช้โมเดล Whisper ใดก็ได้ โมเดล faster-whisper (CTranslate2) ใช้ได้ทันที ส่วนโมเดลทั่วไป (transformers) จะถูกแปลงให้เอง ลิงก์ตรงไปยัง .zip หรือ .tar.gz ที่มีโมเดลก็ใช้ได้
add_model_placeholder|เช่น Systran/faster-whisper-large-v3
download|ดาวน์โหลด
suggestions|แนะนำ:
browse_hf|ดูโมเดล Whisper บน Hugging Face
vram_hint|โมเดลใหญ่แม่นยำกว่าแต่ใช้หน่วยความจำการ์ดจอมากกว่า: small ≈ 1 GB, medium ≈ 2 GB, large ≈ 4 GB
keep_open|เปิดหน้านี้ค้างไว้จนกว่าจะดาวน์โหลดเสร็จ
job_downloading|กำลังดาวน์โหลด… {0} จาก {1}
job_downloading_nosize|กำลังดาวน์โหลด… {0}
job_converting|กำลังแปลงเป็นรูปแบบ faster-whisper…
job_extracting|กำลังแตกไฟล์…
job_ready|ติดตั้งแล้ว
job_error|ล้มเหลว: {0}
retry|ลองอีกครั้ง
plain_server_hint|นี่คือเซิร์ฟเวอร์ WhisperLive มาตรฐาน: พิมพ์ขนาดโมเดล (tiny, base, small, medium, large-v3, large-v3-turbo) แล้วเซิร์ฟเวอร์จะดาวน์โหลดในครั้งแรก หากต้องการดาวน์โหลดโมเดลใดก็ได้จากที่นี่ ให้ติดตั้งส่วนเสริม StreamRemaster บนเซิร์ฟเวอร์
model_name|ชื่อโมเดล
save|บันทึก
saved|บันทึกแล้ว
reset_position|รีเซ็ตตำแหน่งคำบรรยาย
position_reset_done|เรียบร้อย: จะกลับไปอยู่ด้านล่าง
section_performance|ประสิทธิภาพ
performance_hint|หากการ์ดจอของเซิร์ฟเวอร์หน่วยความจำไม่พอ (คำบรรยายไม่มาหรือมีคำเตือนเรื่องหน่วยความจำ) สองตัวเลือกนี้ช่วยคืนพื้นที่ได้มาก ใช้ได้กับเซิร์ฟเวอร์ StreamRemaster เท่านั้น
precision|ความแม่นยำของโมเดล
precision_auto|อัตโนมัติ
precision_int8|ประหยัดหน่วยความจำ (int8)
precision_hint|int8 ใช้หน่วยความจำกราฟิกราวครึ่งหนึ่ง และในทางปฏิบัติเขียนข้อความเหมือนเดิม
translator_device|ตัวแปลทำงานบน
device_gpu|การ์ดจอ
device_cpu|ซีพียู (CPU)
translator_device_hint|บนซีพียูจะคืนหน่วยความจำกราฟิก แต่คำบรรยายที่แปลแล้วจะมาช้าขึ้นเล็กน้อย
interface_lang|ภาษาของหน้าตาโปรแกรม
lang_auto|ตามเบราว์เซอร์
about_text|เปิดเผยซอร์สโค้ด (สัญญาอนุญาต PolyForm Noncommercial) เสียงจะส่งไปยังเซิร์ฟเวอร์ที่คุณตั้งไว้ที่นี่เท่านั้น ไม่มีการส่งไปที่อื่น
about_based|พัฒนาจาก WhisperLive ของ Collabora
source_code|ซอร์สโค้ด
subtitle_preview|คำบรรยายของคุณจะมีหน้าตาแบบนี้
err_invalid_source|นี่ไม่ใช่ชื่อโมเดลของ Hugging Face และไม่ใช่ลิงก์
err_unsupported_url|ใช้ได้เฉพาะลิงก์ Hugging Face หรือลิงก์ตรงไปยังไฟล์ .zip / .tar.gz
err_repo_not_found|ไม่มีโมเดลนี้บน Hugging Face (ตรวจชื่ออีกครั้ง)
err_gated_repo|โมเดลนี้ต้องยอมรับเงื่อนไขบน Hugging Face เซิร์ฟเวอร์ต้องมี HF_TOKEN
err_not_whisper|นี่ไม่ใช่โมเดล Whisper
err_no_weights|ที่เก็บนี้ไม่มีค่าน้ำหนักของโมเดล
err_network_error|เครือข่ายผิดพลาด ลองอีกครั้ง: จะทำต่อจากจุดที่หยุด
err_download_failed|ดาวน์โหลดไม่สำเร็จ
err_convert_failed|แปลงโมเดลไม่ได้
err_bad_archive|ไฟล์บีบอัดเสียหายหรือไม่ปลอดภัย
err_already_downloading|กำลังดาวน์โหลดอยู่แล้ว
err_already_installed|ติดตั้งแล้ว
err_management_disabled|เซิร์ฟเวอร์นี้ปิดการจัดการโมเดลไว้
err_is_default|นี่คือโมเดลค่าเริ่มต้นของเซิร์ฟเวอร์ ลบจากที่นี่ไม่ได้
err_in_use|มีการถอดความที่กำลังทำงานใช้อยู่
err_not_found|โมเดลนี้ไม่อยู่บนเซิร์ฟเวอร์แล้ว
err_server_error|เซิร์ฟเวอร์ผิดพลาด
err_unreachable|ติดต่อเซิร์ฟเวอร์ไม่ได้
err_timeout|เซิร์ฟเวอร์ไม่ตอบกลับทันเวลา
err_unknown|ข้อผิดพลาดที่ไม่คาดคิด ({0})
updates|การอัปเดต
check_updates|ตรวจหาการอัปเดต
check_again|ตรวจอีกครั้ง
update_now|อัปเดต
update_available|มีเวอร์ชัน {0} แล้ว (คุณใช้ {1})
update_latest|คุณใช้เวอร์ชันล่าสุดแล้ว ({0})
update_rate_limited|GitHub จำกัดการตรวจสอบชั่วคราว ลองใหม่ภายหลัง
update_failed|ตรวจหาการอัปเดตไม่ได้ ตรวจสอบการเชื่อมต่อแล้วลองใหม่
update_how_firefox|Firefox ติดตั้งเวอร์ชันใหม่ให้เอง หากต้องการทันที ให้เปิด about:addons คลิกไอคอนเฟือง แล้วเลือก “ตรวจสอบการอัปเดต” เวอร์ชันที่เพิ่งออกอาจใช้เวลาสองสามวันกว่าจะขึ้นบนเว็บไซต์ส่วนเสริม
update_how_chromium|วิธีอัปเดต: ดาวน์โหลดไฟล์ zip สำหรับ Chromium จากหน้าของเวอร์ชัน แตกไฟล์ทับโฟลเดอร์เดิม แล้วกดไอคอนโหลดใหม่บนการ์ด StreamRemaster ใน chrome://extensions การตั้งค่าของคุณจะยังอยู่
update_privacy|การตรวจสอบจะถาม GitHub เพียงหมายเลขเวอร์ชันล่าสุด ไม่มีการส่งข้อมูลอื่นใด
server_update_available|เซิร์ฟเวอร์ของคุณเป็นเวอร์ชัน {0} และมีเวอร์ชัน {1} แล้ว หากต้องการอัปเดต ให้รันคำสั่งนี้บนคอมพิวเตอร์ที่เซิร์ฟเวอร์ทำงานอยู่:
server_version_unknown|เซิร์ฟเวอร์ของคุณไม่ได้บอกเวอร์ชัน จึงเก่ากว่าการตรวจสอบนี้ หากต้องการอัปเดต ให้รันคำสั่งนี้บนคอมพิวเตอร์ที่เซิร์ฟเวอร์ทำงานอยู่:
server_update_latest|เซิร์ฟเวอร์ของคุณเป็นเวอร์ชันล่าสุดแล้ว ({0})
server_update_note|โมเดลยังอยู่ในวอลุ่มของ Docker และไม่ต้องดาวน์โหลดใหม่ หากคุณแก้ไข docker-compose.yml แล้ว git pull แจ้งข้อผิดพลาด ให้รัน git stash ก่อน และ git stash pop หลังจากนั้น
setup_or|หรือ
use_local|ใช้คอมพิวเตอร์เครื่องนี้
use_local_hint|Whisper ทำงานบนการ์ดจอของคอมพิวเตอร์เครื่องนี้ ไม่ต้องใช้เซิร์ฟเวอร์ ดาวน์โหลดโมเดลครั้งเดียวในการตั้งค่า
local_footer|คอมพิวเตอร์เครื่องนี้
local_none|ยังไม่มีโมเดล: ดาวน์โหลดสักตัว
local_intro|Whisper ทำงานในเบราว์เซอร์บนการ์ดจอของคุณ (WebGPU) แต่ละโมเดลดาวน์โหลดจาก Hugging Face ครั้งเดียวและเก็บไว้ในเบราว์เซอร์ โมเดลที่ใหญ่กว่าจะแม่นยำกว่าและใช้หน่วยความจำการ์ดจอมากกว่า
local_sizes|ดาวน์โหลด {0} · ใช้พื้นที่ {1} · หน่วยความจำการ์ดจอประมาณ {2}
local_progress|กำลังดาวน์โหลด… {0} จาก {1}
local_cancel|ยกเลิก
local_gpu|การ์ดจอ: {0}
badge_downloaded|ดาวน์โหลดแล้ว
error_no_webgpu|เบราว์เซอร์นี้ใช้การ์ดจอ (WebGPU) ไม่ได้ จึงถอดเสียงบนคอมพิวเตอร์เครื่องนี้ไม่ได้
error_local_missing|ดาวน์โหลดโมเดลก่อนที่ การตั้งค่า → โมเดลบนคอมพิวเตอร์เครื่องนี้
error_local_failed|การถอดเสียงบนคอมพิวเตอร์เครื่องนี้หยุดเพราะเกิดข้อผิดพลาด
error_local_vram|⚠ หน่วยความจำการ์ดจอของเครื่องนี้ไม่พอสำหรับโมเดลนี้ เลือกโมเดลที่เล็กกว่า
local_download_failed|ดาวน์โหลดไม่สำเร็จ ({0})
local_confirm_delete|ลบโมเดล {0} ออกจากคอมพิวเตอร์เครื่องนี้ไหม? จะได้พื้นที่คืน {1}
local_only_english|บนคอมพิวเตอร์เครื่องนี้ แปลคำบรรยายได้เป็นภาษาอังกฤษเท่านั้น
"""

LANGS['hi'] = """
error_local_lost|ग्राफ़िक्स कार्ड ने ट्रांसक्रिप्शन मॉडल को लगातार कई बार रोक दिया।
fg_hq_badge|शक्तिशाली ग्राफ़िक्स कार्ड के लिए
where_fg_models|मॉडल कहाँ हैं
fg_local_title|इस कंप्यूटर पर स्मूद वीडियो मॉडल
fg_server_title|सर्वर पर स्मूद वीडियो मॉडल
fg_server_intro|सर्वर इन्हें सिर्फ़ रखता है: चुना गया मॉडल उससे डाउनलोड होकर इस कंप्यूटर के ग्राफ़िक्स कार्ड पर चलता है।
fg_server_none|सर्वर पर अभी कोई स्मूद वीडियो मॉडल नहीं है।
fg_server_old|यह सर्वर स्मूद वीडियो मॉडल नहीं रखता: इसे नवीनतम संस्करण पर अपडेट करें।
fg_add_server_title|सर्वर में जोड़ें
fg_server_loading|सर्वर से मॉडल डाउनलोड हो रहा है…
section_transcription|ट्रांसक्रिप्शन मॉडल
transcription_intro|चुनें कि बोली को टेक्स्ट में कहाँ बदला जाए: WhisperLive सर्वर पर या इस कंप्यूटर के ग्राफ़िक्स कार्ड पर।
where_transcribe|कहाँ ट्रांसक्राइब करें
engine_server|सर्वर पर
engine_local|इस कंप्यूटर पर
trans_server_title|सर्वर पर ट्रांसक्रिप्शन मॉडल
trans_local_title|इस कंप्यूटर पर ट्रांसक्रिप्शन मॉडल
badge_in_use|उपयोग में
fg_downloaded_title|डाउनलोड किए गए
fg_add_title|मॉडल जोड़ें
fg_add_url_placeholder|मॉडल फ़ाइल का पता (.stmodel)
fg_download_failed|डाउनलोड नहीं हो सका ({0})। ब्राउज़र से फ़ाइल डाउनलोड करें और इसे इस कंप्यूटर से चुनें।
fg_memory|ग्राफ़िक्स मेमोरी: 1080p वीडियो के साथ लगभग {0}
fg_memory_4k|1080p से 4K पर अपस्केल करते समय लगभग {0}
fg_memory_now|उपयोग में ग्राफ़िक्स मेमोरी: लगभग {0}
fg_file_size|फ़ाइल: {0}
fg_options|विकल्प
fg_sharpen|शार्पनेस
fg_sharpen_off|बंद
fg_sharpen_soft|हल्की
fg_sharpen_medium|मध्यम
fg_sharpen_strong|तेज़
fg_resolution|अपस्केलिंग का लक्ष्य रिज़ॉल्यूशन
fg_res_original|मूल (बिना अपस्केलिंग)
fg_model|स्मूद वीडियो मॉडल
fg_kind_sr|केवल अपस्केलिंग
fg_kind_fi|केवल बीच के फ़्रेम
fg_builtin|अंतर्निहित
fg_model_none|कोई नहीं (AI के बिना)
section_fgmodels|स्मूद वीडियो मॉडल
fg_models_hint|स्मूद वीडियो हमेशा इस कंप्यूटर के ग्राफ़िक्स कार्ड पर चलता है। StreamRemaster एक्सटेंशन के साथ आता है; दूसरे मॉडल इस कंप्यूटर पर या आपके सर्वर पर रह सकते हैं।
fg_add_model|इस कंप्यूटर से फ़ाइल चुनें
fg_no_models|अभी तक कोई मॉडल डाउनलोड नहीं किया गया।
fg_model_bad|यह फ़ाइल मान्य मॉडल नहीं है।
tab_subs|उपशीर्षक
tab_fg|स्मूद वीडियो
fg_start|स्मूद वीडियो चालू करें
fg_stop|स्मूद वीडियो बंद करें
fg_target|लक्ष्य फ़्रेम दर
fg_target_display|स्क्रीन के अनुसार
fg_state_off|बंद
fg_state_measuring|वीडियो माप रहे हैं…
fg_state_on|{0} fps (वीडियो {1} fps)
fg_no_video|इस पेज पर कोई वीडियो नहीं चल रहा है।
fg_no_webgpu|यह ब्राउज़र इसके लिए GPU का उपयोग नहीं कर सकता (WebGPU उपलब्ध नहीं है)।
fg_cannot_read|यह वीडियो पढ़ा नहीं जा सकता: यह सुरक्षित है या किसी अन्य साइट से है।
fg_unavailable|यह पेज एक्सटेंशन की अनुमति नहीं देता।
fg_auto_start|वीडियो चलने पर स्मूद वीडियो अपने आप चालू करें
subs_auto_start|वीडियो चलने पर उपशीर्षक अपने आप शुरू करें
auto_start_hint|इस ब्राउज़र में यह केवल उन टैब में काम करता है जिनमें आपने एक्सटेंशन का बटन क्लिक किया है, जब तक वे किसी दूसरी साइट पर नहीं जाते।
fg_allow_all_sites|सभी साइटों पर अनुमति दें
extName|StreamRemaster
extDescription|किसी भी टैब के लिए लाइव सबटाइटल, जिन्हें आपका अपना Whisper सर्वर लिखता और अनुवाद करता है।
start|सबटाइटल चालू करें
stop|सबटाइटल बंद करें
status_idle|तैयार
status_connecting|कनेक्ट हो रहा है…
status_loading|मॉडल लोड हो रहा है…
status_listening|सुन रहा है…
status_live|लाइव
status_stalled|ऑडियो रुक गया
status_error|त्रुटि
status_noresponse|कोई जवाब नहीं
model|ट्रांसक्रिप्शन मॉडल
model_server_default|सर्वर का डिफ़ॉल्ट
model_default_tag|{0} · डिफ़ॉल्ट
manage_models|मॉडल प्रबंधित करें
spoken_lang|ऑडियो की भाषा
auto_detect|अपने-आप पहचानें
detected|पहचानी गई: {0}
subs_lang|सबटाइटल की भाषा
original_lang|अनुवाद नहीं
lines|पंक्तियाँ
text_size|टेक्स्ट का आकार
save_srt|बंद करते समय सबटाइटल (.srt) सेव करें
advanced|उन्नत
use_vad|ख़ामोशी छोड़ें (आवाज़ की पहचान)
settings|सेटिंग
first_load_hint|पहली बार मॉडल लोड होने में एक मिनट तक लग सकता है।
options_locked|ये विकल्प बदलने के लिए सबटाइटल बंद करें।
server_setup_title|अपना सर्वर कनेक्ट करें
server_setup_hint|StreamRemaster आपके कंप्यूटर या नेटवर्क के WhisperLive सर्वर से, या इस कंप्यूटर के ग्राफ़िक्स कार्ड से ट्रांसक्राइब करता है।
server_address|सर्वर का पता
server_placeholder|जैसे localhost:9090 या 192.168.1.10:9090
connect|कनेक्ट करें
server_ok_models|कनेक्ट हो गया · {0} मॉडल
server_ok_one_model|कनेक्ट हो गया · 1 मॉडल
server_plain|कनेक्ट हो गया · सामान्य WhisperLive (मॉडल प्रबंधन नहीं)
server_checking|जाँच हो रही है…
server_unreachable|सर्वर से कनेक्ट नहीं हो पा रहा। क्या वह चालू है? पता और फ़ायरवॉल जाँचें।
server_timeout|सर्वर ने समय पर जवाब नहीं दिया।
server_bad_url|यह पता सही नहीं है।
server_change|बदलें
server_help|सर्वर कैसे सेट करें?
server_help_1|आपको किसी कंप्यूटर पर WhisperLive सर्वर (मुफ़्त और ओपन सोर्स) चलाना होगा, अच्छा हो कि NVIDIA ग्राफ़िक्स कार्ड हो। छोटे मॉडल सिर्फ़ प्रोसेसर पर भी चलते हैं।
server_help_2|फिर उसका पता यहाँ लिखें: कंप्यूटर का IP और पोर्ट, जैसे 192.168.1.10:9090। अगर इसी कंप्यूटर पर है, तो localhost:9090।
server_help_3|इस पेज से मॉडल डाउनलोड और प्रबंधित करने के लिए सर्वर में StreamRemaster ऐड-ऑन जोड़ें।
server_help_guide|क़दम-दर-क़दम गाइड
error_capture|यह टैब कैप्चर नहीं हो सकता (ब्राउज़र के पेज, एक्सटेंशन स्टोर और PDF की अनुमति नहीं)।
error_no_media|इस पेज पर न वीडियो है न ऑडियो।
error_server_full|सर्वर व्यस्त है। अनुमानित इंतज़ार: {0} मिनट।
error_disconnected|सर्वर ने कनेक्शन बंद कर दिया।
error_model_load|⚠ इस मॉडल के लिए सर्वर पर ग्राफ़िक्स मेमोरी (VRAM) काफ़ी नहीं है। छोटा मॉडल चुनें या उन्नत में “मेमोरी बचाएँ (int8)” चालू करें।
warn_no_response|⚠ आवाज़ होते हुए भी सबटाइटल आने बंद हो गए। शायद मॉडल सर्वर की ग्राफ़िक्स मेमोरी (VRAM) में नहीं समा रहा: छोटा मॉडल चुनें या उन्नत में “मेमोरी बचाएँ (int8)” चालू करें।
warn_slow_load|⚠ मॉडल लोड होने में बहुत देर लग रही है। शायद वह सर्वर की ग्राफ़िक्स मेमोरी (VRAM) में नहीं समाता: छोटा मॉडल चुनें या उन्नत में “मेमोरी बचाएँ (int8)” चालू करें।
error_reload|पेज फिर से लोड करें (F5) और दोबारा शुरू करें।
error_no_server|पहले सर्वर सेट करें।
settings_title|StreamRemaster · सेटिंग
section_subtitles|सबटाइटल
section_interface|इंटरफ़ेस
section_about|परिचय
installed_models|सर्वर पर इंस्टॉल
no_models|अभी कोई मॉडल इंस्टॉल नहीं है।
badge_default|डिफ़ॉल्ट
badge_loaded|मेमोरी में
badge_selected|चुना गया
use_model|इस्तेमाल करें
delete_model|मिटाएँ
confirm_delete|सर्वर से {0} मिटाएँ? इससे {1} खाली होगा।
add_model|मॉडल जोड़ें
add_model_hint|Hugging Face के किसी मॉडल का नाम या लिंक चिपकाएँ। कोई भी Whisper मॉडल चलेगा: faster-whisper (CTranslate2) मॉडल सीधे इस्तेमाल होते हैं और सामान्य (transformers) मॉडल अपने-आप बदल दिए जाते हैं। किसी मॉडल वाली .zip या .tar.gz का सीधा लिंक भी चलेगा।
add_model_placeholder|जैसे Systran/faster-whisper-large-v3
download|डाउनलोड करें
suggestions|सुझाव:
browse_hf|Hugging Face पर Whisper मॉडल देखें
vram_hint|बड़े मॉडल ज़्यादा सटीक हैं पर ज़्यादा ग्राफ़िक्स मेमोरी लेते हैं: small ≈ 1 GB, medium ≈ 2 GB, large ≈ 4 GB।
keep_open|डाउनलोड पूरा होने तक यह पेज खुला रखें।
job_downloading|डाउनलोड हो रहा है… {0} में से {1}
job_downloading_nosize|डाउनलोड हो रहा है… {0}
job_converting|faster-whisper फ़ॉर्मैट में बदला जा रहा है…
job_extracting|खोला जा रहा है…
job_ready|इंस्टॉल हो गया
job_error|विफल: {0}
retry|फिर कोशिश करें
plain_server_hint|यह सामान्य WhisperLive सर्वर है: मॉडल का आकार लिखें (tiny, base, small, medium, large-v3, large-v3-turbo) और सर्वर पहली बार उसे डाउनलोड कर लेगा। यहाँ से कोई भी मॉडल डाउनलोड करने के लिए सर्वर पर StreamRemaster ऐड-ऑन इंस्टॉल करें।
model_name|मॉडल का नाम
save|सेव करें
saved|सेव हो गया
reset_position|सबटाइटल की जगह रीसेट करें
position_reset_done|हो गया: वे फिर नीचे आ जाएँगे।
section_performance|प्रदर्शन
performance_hint|अगर सर्वर के ग्राफ़िक्स कार्ड की मेमोरी कम पड़ जाए (सबटाइटल न आएँ या मेमोरी की चेतावनी दिखे), तो ये दो विकल्प काफ़ी मेमोरी खाली करते हैं। ये सिर्फ़ StreamRemaster सर्वर के साथ काम करते हैं।
precision|मॉडल की सटीकता
precision_auto|अपने-आप
precision_int8|मेमोरी बचाएँ (int8)
precision_hint|int8 लगभग आधी ग्राफ़िक्स मेमोरी लेता है और असल में वही टेक्स्ट लिखता है।
translator_device|अनुवादक कहाँ चलता है
device_gpu|ग्राफ़िक्स कार्ड
device_cpu|प्रोसेसर (CPU)
translator_device_hint|प्रोसेसर पर चलाने से ग्राफ़िक्स मेमोरी खाली होती है, पर अनुवादित सबटाइटल थोड़ा देर से आते हैं।
interface_lang|इंटरफ़ेस की भाषा
lang_auto|ब्राउज़र जैसी
about_text|सोर्स कोड उपलब्ध (PolyForm Noncommercial लाइसेंस)। ऑडियो सिर्फ़ उसी सर्वर पर जाता है जो आप यहाँ सेट करते हैं; और कहीं कुछ नहीं भेजा जाता।
about_based|Collabora के WhisperLive पर आधारित।
source_code|सोर्स कोड
subtitle_preview|आपके सबटाइटल ऐसे दिखेंगे।
err_invalid_source|यह न तो Hugging Face का मॉडल नाम है न लिंक।
err_unsupported_url|सिर्फ़ Hugging Face के लिंक या .zip / .tar.gz फ़ाइलों के सीधे लिंक।
err_repo_not_found|Hugging Face पर यह मॉडल नहीं है (नाम जाँचें)।
err_gated_repo|इस मॉडल के लिए Hugging Face पर शर्तें माननी होती हैं; सर्वर को HF_TOKEN चाहिए।
err_not_whisper|यह Whisper मॉडल नहीं है।
err_no_weights|इस रिपॉज़िटरी में मॉडल के वेट नहीं हैं।
err_network_error|नेटवर्क त्रुटि। फिर कोशिश करें: जहाँ रुका था वहीं से चलेगा।
err_download_failed|डाउनलोड विफल रहा।
err_convert_failed|मॉडल बदला नहीं जा सका।
err_bad_archive|संग्रह फ़ाइल ख़राब है या सुरक्षित नहीं है।
err_already_downloading|यह पहले से डाउनलोड हो रहा है।
err_already_installed|यह पहले से इंस्टॉल है।
err_management_disabled|इस सर्वर पर मॉडल प्रबंधन बंद है।
err_is_default|यह सर्वर का डिफ़ॉल्ट मॉडल है; इसे यहाँ से मिटाया नहीं जा सकता।
err_in_use|चल रहा ट्रांसक्रिप्शन इसे इस्तेमाल कर रहा है।
err_not_found|यह मॉडल अब सर्वर पर नहीं है।
err_server_error|सर्वर त्रुटि।
err_unreachable|सर्वर से कनेक्ट नहीं हो पा रहा।
err_timeout|सर्वर ने समय पर जवाब नहीं दिया।
err_unknown|अनपेक्षित त्रुटि ({0})।
updates|अपडेट
check_updates|अपडेट देखें
check_again|फिर से देखें
update_now|अपडेट करें
update_available|संस्करण {0} उपलब्ध है (आपके पास {1} है)।
update_latest|आपके पास नवीनतम संस्करण है ({0})।
update_rate_limited|GitHub कुछ समय के लिए जाँच सीमित कर रहा है। बाद में फिर कोशिश करें।
update_failed|अपडेट की जाँच नहीं हो सकी। कनेक्शन जाँचें और फिर कोशिश करें।
update_how_firefox|Firefox नए संस्करण अपने आप इंस्टॉल करता है। अभी पाने के लिए about:addons खोलें, गियर आइकन पर क्लिक करें और “अपडेट के लिए जाँचें” चुनें। अभी-अभी आया संस्करण ऐड-ऑन साइट पर पहुँचने में कुछ दिन ले सकता है।
update_how_chromium|अपडेट करने के लिए संस्करण के पेज से Chromium वाली zip डाउनलोड करें, उसे पुराने फ़ोल्डर के ऊपर अनज़िप करें और chrome://extensions में StreamRemaster के कार्ड पर रीलोड आइकन दबाएँ। आपकी सेटिंग्स बनी रहती हैं।
update_privacy|जाँच में GitHub से सिर्फ़ नवीनतम संस्करण का नंबर पूछा जाता है; और कुछ नहीं भेजा जाता।
server_update_available|आपके सर्वर पर संस्करण {0} है और {1} उपलब्ध है। अपडेट करने के लिए, जिस कंप्यूटर पर सर्वर चलता है वहाँ यह चलाएँ:
server_version_unknown|आपका सर्वर अपना संस्करण नहीं बताता, यानी वह इस जाँच से पुराना है। अपडेट करने के लिए, जिस कंप्यूटर पर सर्वर चलता है वहाँ यह चलाएँ:
server_update_latest|आपका सर्वर अप-टू-डेट है ({0})।
server_update_note|मॉडल Docker वॉल्यूम में रहते हैं और दोबारा डाउनलोड नहीं होते। अगर आपने docker-compose.yml बदला है और git pull त्रुटि देता है, तो पहले git stash और बाद में git stash pop चलाएँ।
setup_or|या
use_local|यह कंप्यूटर इस्तेमाल करें
use_local_hint|Whisper इस कंप्यूटर के ग्राफ़िक्स कार्ड पर चलता है, बिना सर्वर के। मॉडल सेटिंग्स में एक बार डाउनलोड होता है।
local_footer|यह कंप्यूटर
local_none|अभी कोई मॉडल नहीं: एक डाउनलोड करें
local_intro|Whisper ब्राउज़र में आपके ग्राफ़िक्स कार्ड (WebGPU) पर चलता है। हर मॉडल Hugging Face से एक बार डाउनलोड होता है और ब्राउज़र में रहता है। बड़े मॉडल बेहतर लिखते हैं और ज़्यादा ग्राफ़िक्स मेमोरी लेते हैं।
local_sizes|डाउनलोड {0} · जगह {1} · लगभग {2} ग्राफ़िक्स मेमोरी
local_progress|डाउनलोड हो रहा है… {0} में से {1}
local_cancel|रद्द करें
local_gpu|ग्राफ़िक्स कार्ड: {0}
badge_downloaded|डाउनलोड हो गया
error_no_webgpu|यह ब्राउज़र ग्राफ़िक्स कार्ड (WebGPU) इस्तेमाल नहीं कर सकता, इसलिए इस कंप्यूटर पर ट्रांसक्राइब नहीं कर सकता।
error_local_missing|पहले सेटिंग्स → इस कंप्यूटर पर मॉडल में एक मॉडल डाउनलोड करें।
error_local_failed|इस कंप्यूटर पर ट्रांसक्रिप्शन एक गड़बड़ी की वजह से रुक गया।
error_local_vram|⚠ इस कंप्यूटर पर इस मॉडल के लिए पर्याप्त ग्राफ़िक्स मेमोरी नहीं है। छोटा मॉडल चुनें।
local_download_failed|डाउनलोड नहीं हो पाया ({0})।
local_confirm_delete|इस कंप्यूटर से {0} मॉडल हटाएँ? इससे {1} खाली होगा।
local_only_english|इस कंप्यूटर पर सबटाइटल का अनुवाद सिर्फ़ अंग्रेज़ी में हो सकता है।
"""

LANGS['ca'] = """
extName|StreamRemaster
extDescription|Subtítols en directe per a qualsevol pestanya, transcrits i traduïts pel teu propi servidor Whisper.
start|Activa els subtítols
stop|Treu els subtítols
status_idle|A punt
status_connecting|Connectant…
status_loading|Carregant el model…
status_listening|Escoltant…
status_live|En directe
status_stalled|Àudio aturat
status_error|Error
status_noresponse|Sense resposta
model|Model de transcripció
model_server_default|El del servidor
model_default_tag|{0} · per defecte
manage_models|Gestiona els models
spoken_lang|Idioma de l'àudio
auto_detect|Automàtic
detected|Detectat: {0}
subs_lang|Subtítols en
original_lang|Sense traduir
lines|Línies
text_size|Mida del text
save_srt|Desa els subtítols (.srt) en aturar
advanced|Avançat
use_vad|Salta els silencis (detecció de veu)
settings|Configuració
first_load_hint|La primera vegada que es carrega un model pot trigar fins a un minut.
options_locked|Treu els subtítols per canviar aquestes opcions.
server_setup_title|Connecta el teu servidor
server_setup_hint|StreamRemaster transcriu amb un servidor WhisperLive al teu ordinador o a la teva xarxa, o amb la targeta gràfica d'aquest ordinador.
server_address|Adreça del servidor
server_placeholder|p. ex. localhost:9090 o 192.168.1.10:9090
connect|Connecta
server_ok_models|Connectat · {0} models
server_ok_one_model|Connectat · 1 model
server_plain|Connectat · WhisperLive estàndard (sense gestió de models)
server_checking|Comprovant…
server_unreachable|No es pot connectar amb el servidor. Està engegat? Revisa l'adreça i el tallafoc.
server_timeout|El servidor no ha respost a temps.
server_bad_url|Aquesta adreça no és vàlida.
server_change|Canvia
server_help|Com munto un servidor?
server_help_1|Necessites un servidor WhisperLive (lliure i gratuït) en un ordinador, millor si té una targeta gràfica NVIDIA. Els models petits també funcionen només amb el processador.
server_help_2|Després escriu aquí la seva adreça: la IP de l'ordinador i el port, p. ex. 192.168.1.10:9090. Si és en aquest mateix ordinador, localhost:9090.
server_help_3|Per baixar i gestionar models des d'aquesta pàgina, afegeix al servidor el complement de StreamRemaster.
server_help_guide|Guia pas a pas
error_capture|No es pot capturar aquesta pestanya (les pàgines del navegador, les botigues d'extensions i els PDF no ho permeten).
error_no_media|No hi ha vídeo ni àudio en aquesta pàgina.
error_server_full|El servidor està ocupat. Espera estimada: {0} min.
error_disconnected|El servidor ha tancat la connexió.
error_model_load|⚠ No hi ha prou memòria gràfica (VRAM) al servidor per a aquest model. Tria un model més petit o activa «Estalvia memòria (int8)» a Avançat.
warn_no_response|⚠ Han deixat d'arribar subtítols tot i que hi ha so. Segurament el model no cap a la memòria gràfica (VRAM) del servidor: tria un model més petit o activa «Estalvia memòria (int8)» a Avançat.
warn_slow_load|⚠ El model triga massa a carregar-se. Pot ser que no càpiga a la memòria gràfica (VRAM) del servidor: tria un model més petit o activa «Estalvia memòria (int8)» a Avançat.
error_reload|Torna a carregar la pàgina (F5) i torna a començar.
error_no_server|Primer configura el servidor.
settings_title|StreamRemaster · Configuració
section_subtitles|Subtítols
section_interface|Interfície
section_about|Quant a
installed_models|Instal·lats al servidor
no_models|Encara no hi ha models instal·lats.
badge_default|Per defecte
badge_loaded|En memòria
badge_selected|Triat
use_model|Fes-lo servir
delete_model|Esborra
confirm_delete|Vols esborrar {0} del servidor? Allibera {1}.
add_model|Afegeix un model
add_model_hint|Enganxa el nom o l'enllaç d'un model de Hugging Face. Serveix qualsevol model Whisper: els de faster-whisper (CTranslate2) es fan servir tal qual i els normals (transformers) es converteixen sols. També serveix un enllaç directe a un .zip o .tar.gz amb un model.
add_model_placeholder|p. ex. Systran/faster-whisper-large-v3
download|Baixa
suggestions|Suggeriments:
browse_hf|Mira models Whisper a Hugging Face
vram_hint|Els models grans encerten més però demanen més memòria de la targeta gràfica: small ≈ 1 GB, medium ≈ 2 GB, large ≈ 4 GB.
keep_open|Deixa aquesta pàgina oberta fins que acabi la baixada.
job_downloading|Baixant… {0} de {1}
job_downloading_nosize|Baixant… {0}
job_converting|Convertint al format de faster-whisper…
job_extracting|Descomprimint…
job_ready|Instal·lat
job_error|Ha fallat: {0}
retry|Torna-ho a provar
plain_server_hint|És un servidor WhisperLive estàndard: escriu una mida de model (tiny, base, small, medium, large-v3, large-v3-turbo) i el servidor el baixa la primera vegada. Per baixar qualsevol model des d'aquí, instal·la el complement de StreamRemaster al servidor.
model_name|Nom del model
save|Desa
saved|Desat
reset_position|Recol·loca els subtítols
position_reset_done|Fet: tornaran a baix.
section_performance|Rendiment
performance_hint|Si la targeta gràfica del servidor es queda sense memòria (els subtítols no arriben o surt un avís de memòria), aquestes dues opcions n'alliberen força. Només funcionen amb el servidor de StreamRemaster.
precision|Precisió del model
precision_auto|Automàtica
precision_int8|Estalvia memòria (int8)
precision_hint|int8 gasta més o menys la meitat de memòria gràfica i, a la pràctica, escriu el mateix text.
translator_device|El traductor va a
device_gpu|La targeta gràfica
device_cpu|El processador (CPU)
translator_device_hint|Al processador allibera memòria gràfica, però els subtítols traduïts arriben una mica més tard.
interface_lang|Idioma de la interfície
lang_auto|El del navegador
about_text|Codi font disponible (llicència PolyForm Noncommercial). L'àudio només va al servidor que configuris aquí; no s'envia res a cap altre lloc.
about_based|Basat en WhisperLive, de Collabora.
source_code|Codi font
subtitle_preview|Així es veuran els teus subtítols.
updates|Actualitzacions
check_updates|Cerca actualitzacions
check_again|Torna a cercar
update_now|Actualitza
update_available|Ja hi ha la versió {0} (tens la {1}).
update_latest|Tens l'última versió ({0}).
update_rate_limited|GitHub està limitant les consultes durant una estona. Torna-ho a provar més tard.
update_failed|No s'han pogut cercar actualitzacions. Revisa la connexió i torna-ho a provar.
update_how_firefox|El Firefox instal·la les versions noves tot sol. Per tenir-la ja, obre about:addons, prem la icona de l'engranatge i tria «Cerca actualitzacions». Una versió acabada de sortir pot trigar uns dies a arribar al web de complements.
update_how_chromium|Per actualitzar, baixa el zip de Chromium de la pàgina de la versió, descomprimeix-lo a sobre de la carpeta antiga i prem la icona de recarregar a la targeta de StreamRemaster de chrome://extensions. La configuració es conserva.
update_privacy|En cercar, només es pregunta a GitHub el número de l'última versió; no s'envia res més.
server_update_available|El teu servidor té la versió {0} i ja hi ha la {1}. Per actualitzar-lo, executa això a l'ordinador on és:
server_version_unknown|El teu servidor no diu quina versió té, així que és anterior a aquesta comprovació. Per actualitzar-lo, executa això a l'ordinador on és:
server_update_latest|El teu servidor està al dia ({0}).
server_update_note|Els models es queden al volum de Docker i no es tornen a baixar. Si has canviat docker-compose.yml i git pull es queixa, executa git stash abans i git stash pop després.
err_invalid_source|Això no és un nom de model de Hugging Face ni un enllaç.
err_unsupported_url|Només enllaços de Hugging Face o enllaços directes a fitxers .zip / .tar.gz.
err_repo_not_found|Aquest model no existeix a Hugging Face (revisa el nom).
err_gated_repo|Aquest model demana acceptar les seves condicions a Hugging Face; el servidor necessita un HF_TOKEN.
err_not_whisper|Això no és un model Whisper.
err_no_weights|Aquest repositori no té els pesos del model.
err_network_error|Error de xarxa. Torna-ho a provar: continua per on anava.
err_download_failed|La baixada ha fallat.
err_convert_failed|No s'ha pogut convertir el model.
err_bad_archive|El fitxer comprimit està malmès o no és segur.
err_already_downloading|Ja s'està baixant.
err_already_installed|Ja està instal·lat.
err_management_disabled|La gestió de models està desactivada en aquest servidor.
err_is_default|És el model per defecte del servidor; no es pot esborrar des d'aquí.
err_in_use|L'està fent servir una transcripció en marxa.
err_not_found|Aquest model ja no és al servidor.
err_server_error|Error del servidor.
err_unreachable|No es pot connectar amb el servidor.
err_timeout|El servidor no ha respost a temps.
err_unknown|Error inesperat ({0}).
fg_sharpen|Nitidesa
fg_sharpen_off|Desactivada
fg_sharpen_soft|Suau
fg_sharpen_medium|Mitjana
fg_sharpen_strong|Forta
auto_start_hint|En aquest navegador només funciona a les pestanyes on hagis fet clic al botó de l'extensió, fins que passin a un altre lloc web.
fg_add_model|Afegeix un fitxer de model
fg_allow_all_sites|Permet-ho a tots els llocs web
fg_auto_start|Activa el vídeo fluid en reproduir-se un vídeo
fg_builtin|Inclòs
fg_cannot_read|No es pot llegir aquest vídeo: està protegit o ve d'un altre lloc.
fg_kind_fi|Fotogrames intermedis
fg_kind_sr|Ampliació
fg_model|Model d'IA
fg_model_bad|Aquest fitxer no és un model vàlid.
fg_model_none|Cap (sense IA)
fg_models_hint|Baixa un fitxer de model (.stmodel, .srmodel, .fimodel) i afegeix-lo aquí. Funciona amb la teva pròpia targeta gràfica.
fg_no_models|Encara no has afegit cap model.
fg_no_video|No s'està reproduint cap vídeo en aquesta pàgina.
fg_no_webgpu|Aquest navegador no pot fer servir la GPU per a això (no té WebGPU).
fg_res_original|Original (sense ampliar)
fg_resolution|Resolució final de l'ampliació
fg_start|Activa el vídeo fluid
fg_state_measuring|Mesurant el vídeo…
fg_state_off|Apagat
fg_state_on|{0} fps (vídeo a {1} fps)
fg_stop|Treu el vídeo fluid
fg_target|FPS desitjats
fg_target_display|Igual que la pantalla
fg_unavailable|Aquesta pàgina no admet extensions.
section_fgmodels|Models de vídeo fluid
subs_auto_start|Inicia els subtítols en reproduir-se un vídeo
tab_fg|Vídeo fluid
tab_subs|Subtítols
badge_downloaded|Baixat
badge_in_use|En ús
engine_local|En aquest ordinador
engine_server|Al servidor
error_local_failed|La transcripció en aquest ordinador s'ha aturat per un error.
error_local_lost|La targeta gràfica ha aturat el model de transcripció diverses vegades seguides.
error_local_missing|Primer baixa un model, a Configuració → Models en aquest ordinador.
error_local_vram|⚠ No hi ha prou memòria gràfica en aquest ordinador per a aquest model. Tria'n un de més petit.
error_no_webgpu|Aquest navegador no pot fer servir la targeta gràfica (WebGPU), així que no pot transcriure en aquest ordinador.
fg_add_server_title|Afegeix al servidor
fg_add_title|Afegeix un model
fg_add_url_placeholder|Adreça d'un fitxer de model (.stmodel)
fg_download_failed|No s'ha pogut baixar ({0}). Baixa el fitxer amb el navegador i tria'l des d'aquest ordinador.
fg_downloaded_title|Baixats
fg_file_size|Fitxer: {0}
fg_hq_badge|Per a targetes gràfiques potents
fg_local_title|Models de vídeo fluid en aquest ordinador
fg_memory|Memòria gràfica: uns {0} amb un vídeo de 1080p
fg_memory_4k|uns {0} ampliant de 1080p a 4K
fg_memory_now|Memòria gràfica en ús: uns {0}
fg_options|Opcions
fg_server_intro|El servidor només els guarda: el model triat es baixa d'allà i funciona a la targeta gràfica d'aquest ordinador.
fg_server_loading|Baixant el model del servidor…
fg_server_none|El servidor encara no té models de vídeo fluid.
fg_server_old|Aquest servidor no guarda models de vídeo fluid: actualitza'l a la darrera versió.
fg_server_title|Models de vídeo fluid al servidor
local_cancel|Cancel·la
local_confirm_delete|Vols esborrar el model {0} d'aquest ordinador? Allibera {1}.
local_download_failed|La baixada ha fallat ({0}).
local_footer|Aquest ordinador
local_gpu|Targeta gràfica: {0}
local_intro|Whisper funciona al navegador, amb la teva targeta gràfica (WebGPU). Cada model es baixa una vegada de Hugging Face i es queda al navegador. Els més grans escriuen millor i necessiten més memòria gràfica.
local_none|Cap model: baixa'n un
local_only_english|En aquest ordinador els subtítols només es poden traduir a l'anglès.
local_progress|Baixant… {0} de {1}
local_sizes|Baixada {0} · ocupa {1} · uns {2} de memòria gràfica
section_transcription|Models de transcripció
setup_or|o
trans_local_title|Models de transcripció en aquest ordinador
trans_server_title|Models de transcripció al servidor
transcription_intro|Tria on es passa la veu a text: en un servidor WhisperLive o a la targeta gràfica d'aquest ordinador.
use_local|Fes servir aquest ordinador
use_local_hint|Whisper funciona amb la targeta gràfica d'aquest ordinador, sense servidor. El model es baixa una vegada, a Configuració.
where_fg_models|On són els models
where_transcribe|On transcriure
"""

LANGS['gl'] = """
extName|StreamRemaster
extDescription|Subtítulos en directo para calquera lapela, transcritos e traducidos polo teu propio servidor Whisper.
start|Activar subtítulos
stop|Quitar subtítulos
status_idle|Listo
status_connecting|Conectando…
status_loading|Cargando o modelo…
status_listening|Escoitando…
status_live|En directo
status_stalled|Audio parado
status_error|Erro
status_noresponse|Sen resposta
model|Modelo de transcrición
model_server_default|O do servidor
model_default_tag|{0} · predeterminado
manage_models|Xestionar modelos
spoken_lang|Idioma do audio
auto_detect|Automático
detected|Detectado: {0}
subs_lang|Subtítulos en
original_lang|Sen traducir
lines|Liñas
text_size|Tamaño do texto
save_srt|Gardar os subtítulos (.srt) ao parar
advanced|Avanzado
use_vad|Saltar silencios (detección de voz)
settings|Axustes
first_load_hint|A primeira vez que se carga un modelo pode tardar ata un minuto.
options_locked|Quita os subtítulos para cambiar estas opcións.
server_setup_title|Conecta o teu servidor
server_setup_hint|StreamRemaster transcribe cun servidor WhisperLive no teu ordenador ou na túa rede, ou coa tarxeta gráfica deste ordenador.
server_address|Enderezo do servidor
server_placeholder|p. ex. localhost:9090 ou 192.168.1.10:9090
connect|Conectar
server_ok_models|Conectado · {0} modelos
server_ok_one_model|Conectado · 1 modelo
server_plain|Conectado · WhisperLive estándar (sen xestión de modelos)
server_checking|Comprobando…
server_unreachable|Non se pode conectar co servidor. Está aceso? Revisa o enderezo e a devasa.
server_timeout|O servidor non respondeu a tempo.
server_bad_url|Ese enderezo non é válido.
server_change|Cambiar
server_help|Como monto un servidor?
server_help_1|Necesitas un servidor WhisperLive (libre e gratuíto) nun ordenador, mellor se ten unha tarxeta gráfica NVIDIA. Os modelos pequenos tamén funcionan só co procesador.
server_help_2|Despois escribe aquí o seu enderezo: a IP do ordenador e o porto, p. ex. 192.168.1.10:9090. Se está neste mesmo ordenador, localhost:9090.
server_help_3|Para descargar e xestionar modelos desde esta páxina, engade ao servidor o complemento de StreamRemaster.
server_help_guide|Guía paso a paso
error_capture|Non se pode capturar esta lapela (as páxinas do navegador, as tendas de extensións e os PDF non o permiten).
error_no_media|Non hai vídeo nin audio nesta páxina.
error_server_full|O servidor está ocupado. Espera estimada: {0} min.
error_disconnected|O servidor pechou a conexión.
error_model_load|⚠ Non hai memoria gráfica (VRAM) abonda no servidor para este modelo. Escolle un modelo máis pequeno ou activa «Aforrar memoria (int8)» en Avanzado.
warn_no_response|⚠ Deixaron de chegar subtítulos aínda que hai son. Seguramente o modelo non cabe na memoria gráfica (VRAM) do servidor: escolle un modelo máis pequeno ou activa «Aforrar memoria (int8)» en Avanzado.
warn_slow_load|⚠ O modelo está a tardar demasiado en cargar. Pode que non caiba na memoria gráfica (VRAM) do servidor: escolle un modelo máis pequeno ou activa «Aforrar memoria (int8)» en Avanzado.
error_reload|Recarga a páxina (F5) e volve empezar.
error_no_server|Primeiro configura o servidor.
settings_title|StreamRemaster · Axustes
section_subtitles|Subtítulos
section_interface|Interface
section_about|Acerca de
installed_models|Instalados no servidor
no_models|Aínda non hai modelos instalados.
badge_default|Predeterminado
badge_loaded|En memoria
badge_selected|Escollido
use_model|Usar
delete_model|Borrar
confirm_delete|Borrar {0} do servidor? Libera {1}.
add_model|Engadir un modelo
add_model_hint|Pega o nome ou a ligazón dun modelo de Hugging Face. Serve calquera modelo Whisper: os de faster-whisper (CTranslate2) úsanse tal cal e os normais (transformers) convértense sós. Tamén serve unha ligazón directa a un .zip ou .tar.gz cun modelo.
add_model_placeholder|p. ex. Systran/faster-whisper-large-v3
download|Descargar
suggestions|Suxestións:
browse_hf|Ver modelos Whisper en Hugging Face
vram_hint|Os modelos grandes acertan máis pero piden máis memoria da tarxeta gráfica: small ≈ 1 GB, medium ≈ 2 GB, large ≈ 4 GB.
keep_open|Deixa esta páxina aberta ata que remate a descarga.
job_downloading|Descargando… {0} de {1}
job_downloading_nosize|Descargando… {0}
job_converting|Convertendo ao formato de faster-whisper…
job_extracting|Descomprimindo…
job_ready|Instalado
job_error|Fallou: {0}
retry|Tentar de novo
plain_server_hint|É un servidor WhisperLive estándar: escribe un tamaño de modelo (tiny, base, small, medium, large-v3, large-v3-turbo) e o servidor descárgao a primeira vez. Para descargar calquera modelo desde aquí, instala o complemento de StreamRemaster no servidor.
model_name|Nome do modelo
save|Gardar
saved|Gardado
reset_position|Recolocar os subtítulos
position_reset_done|Feito: volverán abaixo.
section_performance|Rendemento
performance_hint|Se a tarxeta gráfica do servidor se queda sen memoria (os subtítulos non chegan ou sae un aviso de memoria), estas dúas opcións liberan bastante. Só funcionan co servidor de StreamRemaster.
precision|Precisión do modelo
precision_auto|Automática
precision_int8|Aforrar memoria (int8)
precision_hint|int8 gasta máis ou menos a metade de memoria gráfica e, na práctica, escribe o mesmo texto.
translator_device|O tradutor vai en
device_gpu|A tarxeta gráfica
device_cpu|O procesador (CPU)
translator_device_hint|No procesador libera memoria gráfica, pero os subtítulos traducidos chegan algo máis tarde.
interface_lang|Idioma da interface
lang_auto|O do navegador
about_text|Código fonte dispoñible (licenza PolyForm Noncommercial). O audio só vai ao servidor que configures aquí; non se envía nada a ningún outro sitio.
about_based|Baseado en WhisperLive, de Collabora.
source_code|Código fonte
subtitle_preview|Así se verán os teus subtítulos.
updates|Actualizacións
check_updates|Buscar actualizacións
check_again|Volver buscar
update_now|Actualizar
update_available|Xa está a versión {0} (tes a {1}).
update_latest|Tes a última versión ({0}).
update_rate_limited|GitHub está a limitar as consultas durante un tempo. Volve tentalo máis tarde.
update_failed|Non se puideron buscar actualizacións. Revisa a conexión e volve tentalo.
update_how_firefox|Firefox instala as versións novas el só. Para tela xa, abre about:addons, preme a icona da roda dentada e escolle «Buscar actualizacións». Unha versión recén saída pode tardar uns días en chegar á web de complementos.
update_how_chromium|Para actualizar, descarga o zip de Chromium da páxina da versión, descomprímeo enriba do cartafol antigo e preme a icona de recargar na tarxeta de StreamRemaster de chrome://extensions. Os axustes consérvanse.
update_privacy|Ao buscar, só se lle pregunta a GitHub o número da última versión; non se envía nada máis.
server_update_available|O teu servidor ten a versión {0} e xa está a {1}. Para actualizalo, executa isto no ordenador onde está:
server_version_unknown|O teu servidor non di que versión ten, así que é anterior a esta comprobación. Para actualizalo, executa isto no ordenador onde está:
server_update_latest|O teu servidor está ao día ({0}).
server_update_note|Os modelos quédanse no volume de Docker e non se volven descargar. Se cambiaches docker-compose.yml e git pull se queixa, executa git stash antes e git stash pop despois.
err_invalid_source|Iso non é un nome de modelo de Hugging Face nin unha ligazón.
err_unsupported_url|Só ligazóns de Hugging Face ou ligazóns directas a ficheiros .zip / .tar.gz.
err_repo_not_found|Ese modelo non existe en Hugging Face (revisa o nome).
err_gated_repo|Ese modelo pide aceptar as súas condicións en Hugging Face; o servidor necesita un HF_TOKEN.
err_not_whisper|Iso non é un modelo Whisper.
err_no_weights|Ese repositorio non ten os pesos do modelo.
err_network_error|Erro de rede. Volve tentalo: segue por onde ía.
err_download_failed|A descarga fallou.
err_convert_failed|Non se puido converter o modelo.
err_bad_archive|O ficheiro comprimido está danado ou non é seguro.
err_already_downloading|Xa se está a descargar.
err_already_installed|Xa está instalado.
err_management_disabled|A xestión de modelos está desactivada neste servidor.
err_is_default|É o modelo predeterminado do servidor; non se pode borrar desde aquí.
err_in_use|Estao a usar unha transcrición en marcha.
err_not_found|Ese modelo xa non está no servidor.
err_server_error|Erro do servidor.
err_unreachable|Non se pode conectar co servidor.
err_timeout|O servidor non respondeu a tempo.
err_unknown|Erro inesperado ({0}).
fg_sharpen|Nitidez
fg_sharpen_off|Desactivada
fg_sharpen_soft|Suave
fg_sharpen_medium|Media
fg_sharpen_strong|Forte
auto_start_hint|Neste navegador só funciona nas lapelas nas que premiches o botón da extensión, ata que pasen a outro sitio web.
fg_add_model|Engadir un ficheiro de modelo
fg_allow_all_sites|Permitir en todos os sitios web
fg_auto_start|Activar o vídeo fluído ao reproducirse un vídeo
fg_builtin|Incluído
fg_cannot_read|Este vídeo non se pode ler: está protexido ou vén doutro sitio.
fg_kind_fi|Fotogramas intermedios
fg_kind_sr|Ampliación
fg_model|Modelo de IA
fg_model_bad|Ese ficheiro non é un modelo válido.
fg_model_none|Ningún (sen IA)
fg_models_hint|Descarga un ficheiro de modelo (.stmodel, .srmodel, .fimodel) e engádeo aquí. Funciona na túa propia tarxeta gráfica.
fg_no_models|Aínda non engadiches ningún modelo.
fg_no_video|Non se está a reproducir ningún vídeo nesta páxina.
fg_no_webgpu|Este navegador non pode usar a GPU para isto (non ten WebGPU).
fg_res_original|Orixinal (sen ampliar)
fg_resolution|Resolución final da ampliación
fg_start|Activar vídeo fluído
fg_state_measuring|Medindo o vídeo…
fg_state_off|Apagado
fg_state_on|{0} fps (vídeo a {1} fps)
fg_stop|Quitar vídeo fluído
fg_target|FPS desexados
fg_target_display|Igual que a pantalla
fg_unavailable|Esta páxina non admite extensións.
section_fgmodels|Modelos de vídeo fluído
subs_auto_start|Iniciar os subtítulos ao reproducirse un vídeo
tab_fg|Vídeo fluído
tab_subs|Subtítulos
badge_downloaded|Descargado
badge_in_use|En uso
engine_local|Neste ordenador
engine_server|No servidor
error_local_failed|A transcrición neste ordenador detívose por un erro.
error_local_lost|A tarxeta gráfica detivo o modelo de transcrición varias veces seguidas.
error_local_missing|Primeiro descarga un modelo, en Axustes → Modelos neste ordenador.
error_local_vram|⚠ Non hai memoria gráfica dabondo neste ordenador para este modelo. Escolle un máis pequeno.
error_no_webgpu|Este navegador non pode usar a tarxeta gráfica (WebGPU), así que non pode transcribir neste ordenador.
fg_add_server_title|Engadir ao servidor
fg_add_title|Engadir un modelo
fg_add_url_placeholder|Enderezo dun ficheiro de modelo (.stmodel)
fg_download_failed|Non se puido descargar ({0}). Descarga o ficheiro co navegador e escólleo desde este ordenador.
fg_downloaded_title|Descargados
fg_file_size|Ficheiro: {0}
fg_hq_badge|Para tarxetas gráficas potentes
fg_local_title|Modelos de vídeo fluído neste ordenador
fg_memory|Memoria gráfica: uns {0} cun vídeo de 1080p
fg_memory_4k|uns {0} ampliando de 1080p a 4K
fg_memory_now|Memoria gráfica en uso: uns {0}
fg_options|Opcións
fg_server_intro|O servidor só os garda: o modelo escollido báixase del e funciona na tarxeta gráfica deste ordenador.
fg_server_loading|Baixando o modelo do servidor…
fg_server_none|O servidor aínda non ten modelos de vídeo fluído.
fg_server_old|Este servidor non garda modelos de vídeo fluído: actualízao á última versión.
fg_server_title|Modelos de vídeo fluído no servidor
local_cancel|Cancelar
local_confirm_delete|Borrar o modelo {0} deste ordenador? Libera {1}.
local_download_failed|A descarga fallou ({0}).
local_footer|Este ordenador
local_gpu|Tarxeta gráfica: {0}
local_intro|Whisper funciona no navegador, coa túa tarxeta gráfica (WebGPU). Cada modelo descárgase unha vez de Hugging Face e queda no navegador. Os máis grandes escriben mellor e precisan máis memoria gráfica.
local_none|Ningún modelo: descarga un
local_only_english|Neste ordenador os subtítulos só se poden traducir ao inglés.
local_progress|Descargando… {0} de {1}
local_sizes|Descarga {0} · ocupa {1} · uns {2} de memoria gráfica
section_transcription|Modelos de transcrición
setup_or|ou
trans_local_title|Modelos de transcrición neste ordenador
trans_server_title|Modelos de transcrición no servidor
transcription_intro|Escolle onde se pasa a voz a texto: nun servidor WhisperLive ou na tarxeta gráfica deste ordenador.
use_local|Usar este ordenador
use_local_hint|Whisper funciona coa tarxeta gráfica deste ordenador, sen servidor. O modelo descárgase unha vez, en Axustes.
where_fg_models|Onde están os modelos
where_transcribe|Onde transcribir
"""

LANGS['eu'] = """
extName|StreamRemaster
extDescription|Zuzeneko azpitituluak edozein fitxatan, zure Whisper zerbitzariak transkribatuak eta itzuliak.
start|Aktibatu azpitituluak
stop|Kendu azpitituluak
status_idle|Prest
status_connecting|Konektatzen…
status_loading|Eredua kargatzen…
status_listening|Entzuten…
status_live|Zuzenean
status_stalled|Audioa geldituta
status_error|Errorea
status_noresponse|Erantzunik ez
model|Transkripzio-eredua
model_server_default|Zerbitzariarena
model_default_tag|{0} · lehenetsia
manage_models|Kudeatu ereduak
spoken_lang|Audioaren hizkuntza
auto_detect|Automatikoa
detected|Hautemana: {0}
subs_lang|Azpitituluen hizkuntza
original_lang|Itzuli gabe
lines|Lerroak
text_size|Testuaren tamaina
save_srt|Gorde azpitituluak (.srt) gelditzean
advanced|Aurreratua
use_vad|Saltatu isiluneak (ahotsa hautematea)
settings|Ezarpenak
first_load_hint|Eredu bat lehen aldiz kargatzeak minutu bat ere iraun dezake.
options_locked|Kendu azpitituluak aukera hauek aldatzeko.
server_setup_title|Konektatu zure zerbitzaria
server_setup_hint|StreamRemaster-ek WhisperLive zerbitzari batekin transkribatzen du, zure ordenagailuan edo sarean, edo ordenagailu honetako txartel grafikoarekin.
server_address|Zerbitzariaren helbidea
server_placeholder|adib. localhost:9090 edo 192.168.1.10:9090
connect|Konektatu
server_ok_models|Konektatuta · {0} eredu
server_ok_one_model|Konektatuta · eredu 1
server_plain|Konektatuta · WhisperLive estandarra (ereduak kudeatu gabe)
server_checking|Egiaztatzen…
server_unreachable|Ezin da zerbitzarira konektatu. Piztuta dago? Berrikusi helbidea eta suebakia.
server_timeout|Zerbitzariak ez du garaiz erantzun.
server_bad_url|Helbide hori ez da baliozkoa.
server_change|Aldatu
server_help|Nola muntatu zerbitzari bat?
server_help_1|WhisperLive zerbitzari bat behar duzu (librea eta doakoa) ordenagailu batean, hobe NVIDIA txartel grafikoa badu. Eredu txikiek prozesadorearekin bakarrik ere funtzionatzen dute.
server_help_2|Gero, idatzi hemen haren helbidea: ordenagailuaren IPa eta ataka, adib. 192.168.1.10:9090. Ordenagailu honetan bertan badago, localhost:9090.
server_help_3|Orri honetatik ereduak deskargatzeko eta kudeatzeko, gehitu StreamRemaster-en osagarria zerbitzarira.
server_help_guide|Urratsez urratseko gida
error_capture|Ezin da fitxa hau kapturatu (nabigatzailearen orriek, gehigarrien dendek eta PDFek ez dute uzten).
error_no_media|Orri honetan ez dago ez bideorik ez audiorik.
error_server_full|Zerbitzaria lanpetuta dago. Gutxi gorabeherako itxaronaldia: {0} min.
error_disconnected|Zerbitzariak konexioa itxi du.
error_model_load|⚠ Zerbitzariak ez du memoria grafiko (VRAM) nahikorik eredu honetarako. Aukeratu eredu txikiago bat edo aktibatu «Aurreztu memoria (int8)» Aurreratua atalean.
warn_no_response|⚠ Azpitituluak ez dira iristen, soinua egon arren. Seguruenik eredua ez da sartzen zerbitzariaren memoria grafikoan (VRAM): aukeratu eredu txikiago bat edo aktibatu «Aurreztu memoria (int8)» Aurreratua atalean.
warn_slow_load|⚠ Ereduak denbora gehiegi behar du kargatzeko. Agian ez da sartzen zerbitzariaren memoria grafikoan (VRAM): aukeratu eredu txikiago bat edo aktibatu «Aurreztu memoria (int8)» Aurreratua atalean.
error_reload|Kargatu berriro orria (F5) eta hasi berriz.
error_no_server|Lehenik, konfiguratu zerbitzaria.
settings_title|StreamRemaster · Ezarpenak
section_subtitles|Azpitituluak
section_interface|Interfazea
section_about|Honi buruz
installed_models|Zerbitzarian instalatuak
no_models|Oraindik ez dago eredurik instalatuta.
badge_default|Lehenetsia
badge_loaded|Memorian
badge_selected|Aukeratua
use_model|Erabili
delete_model|Ezabatu
confirm_delete|{0} zerbitzaritik ezabatu? {1} askatuko dira.
add_model|Gehitu eredu bat
add_model_hint|Itsatsi Hugging Face-ko eredu baten izena edo esteka. Edozein Whisper eredu balio du: faster-whisper-enak (CTranslate2) bere horretan erabiltzen dira, eta arruntak (transformers) berez bihurtzen dira. Eredu bat duen .zip edo .tar.gz baterako esteka zuzena ere balio du.
add_model_placeholder|adib. Systran/faster-whisper-large-v3
download|Deskargatu
suggestions|Iradokizunak:
browse_hf|Ikusi Whisper ereduak Hugging Face-n
vram_hint|Eredu handiek gehiago asmatzen dute, baina txartel grafikoaren memoria gehiago behar dute: small ≈ 1 GB, medium ≈ 2 GB, large ≈ 4 GB.
keep_open|Utzi orri hau irekita deskarga amaitu arte.
job_downloading|Deskargatzen… {0} / {1}
job_downloading_nosize|Deskargatzen… {0}
job_converting|faster-whisper formatura bihurtzen…
job_extracting|Deskonprimatzen…
job_ready|Instalatuta
job_error|Huts egin du: {0}
retry|Saiatu berriro
plain_server_hint|WhisperLive zerbitzari estandar bat da: idatzi eredu-tamaina bat (tiny, base, small, medium, large-v3, large-v3-turbo) eta zerbitzariak lehen aldian deskargatuko du. Hemendik edozein eredu deskargatzeko, instalatu StreamRemaster-en osagarria zerbitzarian.
model_name|Ereduaren izena
save|Gorde
saved|Gordeta
reset_position|Kokatu berriro azpitituluak
position_reset_done|Eginda: behera itzuliko dira.
section_performance|Errendimendua
performance_hint|Zerbitzariko txartel grafikoa memoriarik gabe geratzen bada (azpitituluak ez dira iristen edo memoria-abisu bat agertzen da), bi aukera hauek asko askatzen dute. StreamRemaster-en zerbitzariarekin bakarrik dabiltza.
precision|Ereduaren zehaztasuna
precision_auto|Automatikoa
precision_int8|Aurreztu memoria (int8)
precision_hint|int8-k memoria grafikoaren erdia inguru erabiltzen du eta, praktikan, testu bera idazten du.
translator_device|Itzultzailea exekutatzeko
device_gpu|Txartel grafikoa
device_cpu|Prozesadorea (CPU)
translator_device_hint|Prozesadorean memoria grafikoa askatzen da, baina itzulitako azpitituluak pixka bat beranduago iristen dira.
interface_lang|Interfazearen hizkuntza
lang_auto|Nabigatzailearena
about_text|Iturburu-kodea eskuragarri (PolyForm Noncommercial lizentzia). Audioa hemen konfiguratzen duzun zerbitzarira bakarrik doa; ez da ezer bidaltzen beste inora.
about_based|WhisperLive-n oinarritua, Collaborarena.
source_code|Iturburu-kodea
subtitle_preview|Horrela ikusiko dira zure azpitituluak.
updates|Eguneratzeak
check_updates|Bilatu eguneratzeak
check_again|Bilatu berriro
update_now|Eguneratu
update_available|{0} bertsioa dago jada ({1} duzu).
update_latest|Azken bertsioa duzu ({0}).
update_rate_limited|GitHub kontsultak mugatzen ari da denbora batez. Saiatu berriro geroago.
update_failed|Ezin izan dira eguneratzeak bilatu. Berrikusi konexioa eta saiatu berriro.
update_how_firefox|Firefoxek berez instalatzen ditu bertsio berriak. Orain bertan izateko, ireki about:addons, sakatu engranajearen ikonoa eta aukeratu «Bilatu eguneratzeak». Argitaratu berri den bertsio batek egun batzuk behar ditzake gehigarrien webgunera iristeko.
update_how_chromium|Eguneratzeko, deskargatu Chromiumeko zip-a bertsioaren orritik, deskonprimatu karpeta zaharraren gainean eta sakatu birkargatzeko ikonoa chrome://extensions orriko StreamRemaster txartelean. Ezarpenak gordetzen dira.
update_privacy|Bilatzean, azken bertsioaren zenbakia bakarrik galdetzen zaio GitHubi; ez da beste ezer bidaltzen.
server_update_available|Zure zerbitzariak {0} bertsioa du eta {1} dago jada. Eguneratzeko, exekutatu hau zerbitzaria dagoen ordenagailuan:
server_version_unknown|Zure zerbitzariak ez du esaten zer bertsio duen; beraz, egiaztapen hau baino zaharragoa da. Eguneratzeko, exekutatu hau zerbitzaria dagoen ordenagailuan:
server_update_latest|Zure zerbitzaria egunean dago ({0}).
server_update_note|Ereduak Dockerren bolumenean geratzen dira eta ez dira berriro deskargatzen. docker-compose.yml aldatu baduzu eta git pull-ek kexa egiten badu, exekutatu git stash aurretik eta git stash pop ondoren.
err_invalid_source|Hori ez da Hugging Face-ko eredu-izen bat, ezta esteka bat ere.
err_unsupported_url|Hugging Face-ko estekak edo .zip / .tar.gz fitxategietarako esteka zuzenak bakarrik.
err_repo_not_found|Eredu hori ez dago Hugging Face-n (berrikusi izena).
err_gated_repo|Eredu horrek bere baldintzak onartzea eskatzen du Hugging Face-n; zerbitzariak HF_TOKEN bat behar du.
err_not_whisper|Hori ez da Whisper eredu bat.
err_no_weights|Biltegi horrek ez ditu ereduaren pisuak.
err_network_error|Sare-errorea. Saiatu berriro: utzitako lekutik jarraituko du.
err_download_failed|Deskargak huts egin du.
err_convert_failed|Ezin izan da eredua bihurtu.
err_bad_archive|Fitxategi konprimatua hondatuta dago edo ez da segurua.
err_already_downloading|Deskargatzen ari da jada.
err_already_installed|Instalatuta dago jada.
err_management_disabled|Ereduen kudeaketa desaktibatuta dago zerbitzari honetan.
err_is_default|Zerbitzariaren eredu lehenetsia da; ezin da hemendik ezabatu.
err_in_use|Martxan dagoen transkripzio bat erabiltzen ari da.
err_not_found|Eredu hori ez dago jada zerbitzarian.
err_server_error|Zerbitzariaren errorea.
err_unreachable|Ezin da zerbitzarira konektatu.
err_timeout|Zerbitzariak ez du garaiz erantzun.
err_unknown|Ustekabeko errorea ({0}).
fg_sharpen|Garbitasuna
fg_sharpen_off|Desaktibatuta
fg_sharpen_soft|Leuna
fg_sharpen_medium|Ertaina
fg_sharpen_strong|Indartsua
auto_start_hint|Nabigatzaile honetan, gehigarriaren botoia sakatu duzun fitxetan bakarrik dabil, beste webgune batera joan arte.
fg_add_model|Gehitu eredu-fitxategi bat
fg_allow_all_sites|Baimendu webgune guztietan
fg_auto_start|Aktibatu bideo leuna bideo bat erreproduzitzean
fg_builtin|Integratua
fg_cannot_read|Ezin da bideo hau irakurri: babestuta dago edo beste webgune batetik dator.
fg_kind_fi|Tarteko fotogramak
fg_kind_sr|Bereizmena handitzea
fg_model|AA eredua
fg_model_bad|Fitxategi hori ez da eredu baliozko bat.
fg_model_none|Bat ere ez (AArik gabe)
fg_models_hint|Deskargatu eredu-fitxategi bat (.stmodel, .srmodel, .fimodel) eta gehitu hemen. Zure txartel grafikoan bertan exekutatzen da.
fg_no_models|Oraindik ez duzu eredurik gehitu.
fg_no_video|Orri honetan ez da bideorik erreproduzitzen ari.
fg_no_webgpu|Nabigatzaile honek ezin du GPUa erabili horretarako (WebGPU ez dago erabilgarri).
fg_res_original|Jatorrizkoa (handitu gabe)
fg_resolution|Helburuko bereizmena
fg_start|Aktibatu bideo leuna
fg_state_measuring|Bideoa neurtzen…
fg_state_off|Itzalita
fg_state_on|{0} fps (bideoa: {1} fps)
fg_stop|Kendu bideo leuna
fg_target|Helburuko FPSak
fg_target_display|Pantailarena
fg_unavailable|Orri honek ez du gehigarririk onartzen.
section_fgmodels|Bideo leunerako ereduak
subs_auto_start|Hasi azpitituluak bideo bat erreproduzitzean
tab_fg|Bideo leuna
tab_subs|Azpitituluak
badge_downloaded|Deskargatuta
badge_in_use|Erabiltzen
engine_local|Ordenagailu honetan
engine_server|Zerbitzarian
error_local_failed|Ordenagailu honetako transkripzioa errore baten ondorioz gelditu da.
error_local_lost|Txartel grafikoak transkripzio-eredua hainbat aldiz jarraian gelditu du.
error_local_missing|Lehenik, deskargatu eredu bat, Ezarpenak → Ordenagailu honetako ereduak atalean.
error_local_vram|⚠ Ordenagailu honek ez du memoria grafiko nahikorik eredu honetarako. Aukeratu txikiago bat.
error_no_webgpu|Nabigatzaile honek ezin du txartel grafikoa erabili (WebGPU), beraz, ezin du ordenagailu honetan transkribatu.
fg_add_server_title|Gehitu zerbitzarira
fg_add_title|Gehitu eredu bat
fg_add_url_placeholder|Eredu-fitxategi baten helbidea (.stmodel)
fg_download_failed|Ezin izan da deskargatu ({0}). Deskargatu fitxategia nabigatzailearekin eta aukeratu ordenagailu honetatik.
fg_downloaded_title|Deskargatuak
fg_file_size|Fitxategia: {0}
fg_hq_badge|Txartel grafiko indartsuetarako
fg_local_title|Ordenagailu honetako bideo leunaren ereduak
fg_memory|Memoria grafikoa: {0} inguru 1080p-ko bideo batekin
fg_memory_4k|{0} inguru 1080p-tik 4K-ra handituz
fg_memory_now|Erabiltzen ari den memoria grafikoa: {0} inguru
fg_options|Aukerak
fg_server_intro|Zerbitzariak gorde besterik ez ditu egiten: aukeratutako eredua bertatik deskargatzen da eta ordenagailu honetako txartel grafikoan dabil.
fg_server_loading|Eredua zerbitzaritik deskargatzen…
fg_server_none|Zerbitzariak oraindik ez du bideo leunaren eredurik.
fg_server_old|Zerbitzari honek ez ditu bideo leunaren ereduak gordetzen: eguneratu azken bertsiora.
fg_server_title|Zerbitzariko bideo leunaren ereduak
local_cancel|Utzi
local_confirm_delete|{0} eredua ordenagailu honetatik ezabatu? {1} askatzen ditu.
local_download_failed|Deskargak huts egin du ({0}).
local_footer|Ordenagailu hau
local_gpu|Txartel grafikoa: {0}
local_intro|Whisper nabigatzailean dabil, zure txartel grafikoarekin (WebGPU). Eredu bakoitza behin deskargatzen da Hugging Facetik eta nabigatzailean geratzen da. Handienek hobeto idazten dute eta memoria grafiko gehiago behar dute.
local_none|Eredurik ez: deskargatu bat
local_only_english|Ordenagailu honetan azpitituluak ingelesera bakarrik itzul daitezke.
local_progress|Deskargatzen… {0} / {1}
local_sizes|Deskarga {0} · {1} hartzen ditu · {2} inguru memoria grafiko
section_transcription|Transkripzio-ereduak
setup_or|edo
trans_local_title|Ordenagailu honetako transkripzio-ereduak
trans_server_title|Zerbitzariko transkripzio-ereduak
transcription_intro|Aukeratu non bihurtzen den ahotsa testu: WhisperLive zerbitzari batean edo ordenagailu honetako txartel grafikoan.
use_local|Erabili ordenagailu hau
use_local_hint|Whisper ordenagailu honetako txartel grafikoarekin dabil, zerbitzaririk gabe. Eredua behin deskargatzen da, Ezarpenetan.
where_fg_models|Non dauden ereduak
where_transcribe|Non transkribatu
"""
