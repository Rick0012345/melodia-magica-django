# Como Usar o Sistema de Questões - Melodia Mágica

## Visão Geral

O sistema agora suporta de forma otimizada dois tipos principais de questões:
- **Múltipla Escolha**: Com alternativas personalizadas
- **Verdadeiro/Falso**: Com sistema simplificado

## Tipos de Questões

### 1. Questões de Múltipla Escolha

**Como criar:**
1. Acesse o Django Admin
2. Vá em "Perguntas" → "Adicionar Pergunta"
3. Preencha:
   - **Pergunta**: O texto da pergunta
   - **Quiz**: Selecione o quiz
   - **Tipo**: Selecione "Múltipla Escolha"
4. Salve a pergunta
5. Na tela de edição, adicione as alternativas:
   - Mínimo de 2 alternativas
   - Marque **exatamente uma** como correta
   - Preencha o texto de cada alternativa

**Exemplo:**
```
Pergunta: "Qual é a capital do Brasil?"
Tipo: Múltipla Escolha

Alternativas:
☐ São Paulo
☐ Rio de Janeiro
☑ Brasília (marcada como correta)
☐ Belo Horizonte
```

### 2. Questões de Verdadeiro/Falso

**Como criar:**
1. Acesse o Django Admin
2. Vá em "Perguntas" → "Adicionar Pergunta"
3. Preencha:
   - **Pergunta**: O texto da pergunta
   - **Quiz**: Selecione o quiz
   - **Tipo**: Selecione "Verdadeiro/Falso"
   - **Resposta Correta**: 
     - ✅ Marque a caixa se a resposta correta for "Verdadeiro"
     - ❌ Deixe desmarcada se a resposta correta for "Falso"

**Exemplo:**
```
Pergunta: "O Brasil é o maior país da América do Sul?"
Tipo: Verdadeiro/Falso
Resposta Correta: ✅ (marcado = Verdadeiro é correto)
```

## Vantagens do Sistema Melhorado

### Para Questões de Verdadeiro/Falso:
- ✅ **Mais simples**: Apenas uma caixa para marcar
- ✅ **Mais rápido**: Não precisa criar alternativas
- ✅ **Menos erro**: Impossível ter configuração inválida
- ✅ **Interface clara**: Indicação visual do que marcar

### Para Questões de Múltipla Escolha:
- ✅ **Flexibilidade total**: Quantas alternativas quiser
- ✅ **Validação automática**: Sistema impede configurações inválidas
- ✅ **Organização**: Alternativas ficam agrupadas com a pergunta

## Validações Automáticas

O sistema verifica automaticamente:

### Múltipla Escolha:
- Mínimo de 2 alternativas
- Exatamente 1 alternativa marcada como correta
- Não permite múltiplas corretas

### Verdadeiro/Falso:
- Campo de resposta deve ser definido
- Não permite alternativas extras

## Status das Questões

Na listagem do admin, você verá:
- ✅ **Válida**: Questão configurada corretamente
- ❌ **Inválida**: Questão precisa ser corrigida

## Dicas Importantes

1. **Para Verdadeiro/Falso**: 
   - Sempre defina se a resposta correta é Verdadeiro ou Falso
   - O sistema mostra claramente qual é a resposta correta

2. **Para Múltipla Escolha**:
   - Adicione alternativas suficientes (pelo menos 2)
   - Marque apenas uma como correta
   - Textos das alternativas devem ser claros

3. **Organização**:
   - Agrupe questões por nível de dificuldade
   - Use descrições claras nos quizzes
   - Teste as questões antes de publicar

## Migração de Questões Antigas

O sistema mantém compatibilidade com questões antigas:
- Questões de verdadeiro/falso antigas continuam funcionando
- Recomenda-se migrar para o novo sistema para melhor experiência

## Exemplo Prático

### Criando um Quiz Completo:

1. **Crie o Quiz**:
   ```
   Título: "Geografia do Brasil"
   Descrição: "Teste seus conhecimentos sobre geografia brasileira"
   Nível: 1
   ```

2. **Adicione Questões Variadas**:
   ```
   Questão 1 (Verdadeiro/Falso):
   "O Brasil faz fronteira com todos os países da América do Sul, exceto Chile e Equador?"
   Resposta: ✅ Verdadeiro

   Questão 2 (Múltipla Escolha):
   "Qual é o maior estado brasileiro em área?"
   ☐ Bahia
   ☐ Minas Gerais
   ☑ Amazonas
   ☐ Pará
   ```

3. **Verifique**:
   - Todas as questões mostram ✅ Válida
   - Respostas corretas estão definidas
   - Quiz está pronto para uso

## Suporte

Em caso de dúvidas sobre o sistema de questões, verifique:
1. Se a questão está marcada como ✅ Válida
2. Se o tipo está correto
3. Se as alternativas/respostas estão definidas

O sistema foi projetado para ser intuitivo e prevenir erros comuns na criação de questões. 