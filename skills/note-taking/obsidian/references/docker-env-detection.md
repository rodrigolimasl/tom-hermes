# Detectando Hermes em ambiente Docker/container

## Sinais de ambiente containerizado

- `HERMES_S6_SUPERVISED_CHILD` está setado no ambiente
- Processo `s6-supervise main-hermes` visível em `ps aux`
- Fonte do Hermes em `/opt/hermes/` (diretório de instalação)
- `HERMES_HOME` em `/opt/data` (padrão Docker)
- `HERMES_SESSION_PLATFORM` indica gateway ativo (telegram, discord, etc.)

## Impacto no Obsidian

O vault sincronizado via Obsidian Cloud Sync fica na máquina host, não no container. O `.obsidian` directory não existe dentro do container.

## Diagnóstico rápido (a usar antes de `find`)

```bash
echo $HERMES_S6_SUPERVISED_CHILD
echo $HERMES_HOME
echo $HERMES_SESSION_PLATFORM
ps aux | grep s6-supervise
```

Se `HERMES_S6_SUPERVISED_CHILD` está setado, está em Docker/container.

## Restrição de configuração

O arquivo `config.yaml` é protegido contra edição pelo agente (security guard). Para alterar:
- O usuário precisa editar manualmente via `hermes config edit` ou editor de texto
- Para habilitar toolsets em gateway, editar seção `platform_toolsets` da config
- Após alterações, reiniciar o gateway com `hermes gateway restart`
- Após ferramentas novas, `/reset` na conversa para recarregar schema de tools

## Exemplo de platform_toolsets

```yaml
platform_toolsets:
  telegram: [web, terminal, file, browser, skills, todo, cronjob, messaging, search, session_search, memory, clarify, delegation]
```

Colocar entre as seções `model` e `auxiliary` do config.yaml.
