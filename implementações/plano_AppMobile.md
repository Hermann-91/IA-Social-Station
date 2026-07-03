# Plano de Evolução: IA Social Station Mobile (Play Store)

Este documento detalha a estratégia para transformar o protótipo IA Social Station em um produto comercializável.

## 1. Nova Arquitetura (Cliente-Servidor)
Para o mobile, abandonaremos o monólito Streamlit em favor de uma estrutura escalável:
- **Backend (API)**: Construído com **FastAPI**. Ele protegerá suas chaves de API e processará as requisições do Gemini.
- **Frontend (Mobile)**: Construído com **Flutter** ou **React Native** para uma experiência nativa no Android/iOS.

## 2. Funcionalidades de Diferenciação
- **Geração Multimodal Nativa**: Integração de APIs de imagem (Imagen 3 ou DALL-E) para gerar o card completo dentro do app.
- **Fluxo "Anti-Ban" Otimizado**: Botão que baixa a imagem, copia a legenda e abre o Instagram na tela de postagem com um clique.
- **Gestão de Personas**: Configuração de "Voz da Marca" para que a IA gere conteúdos personalizados para diferentes nichos.

## 3. Estratégia de Monetização
- **Sistema de Créditos**: O usuário compra pacotes de "Gerações" (ex: 30 posts por R$ 14,90).
- **Assinatura Premium**: Acesso ilimitado e agendamento de posts com notificações push.

## 4. Cronograma de Implementação
1. **Fase API**: Refatorar o `engine.py` para funcionar como um serviço web.
2. **Fase Protótipo**: Desenvolver a interface de cards no Flutter.
3. **Fase Lançamento**: Configurar pagamentos na Play Store.
