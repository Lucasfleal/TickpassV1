#!/bin/bash

# Configurações
DB_NAME="TICKPASS"
DB_USER="root"
DB_PASS="Yig9VEUiVwC_uPl"
CONTAINER_NAME="mysqldb"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="backup/backup_meubanco_$TIMESTAMP.sql"

# Executa o mysqldump dentro do container
docker exec -i $CONTAINER_NAME mysqldump -u $DB_USER -p$DB_PASS $DB_NAME > $OUTPUT_FILE

# Mensagem de confirmação
if [ $? -eq 0 ]; then
  echo "Backup do banco de dados $DB_NAME foi salvo em $OUTPUT_FILE"
else
  echo "Falha ao realizar o backup do banco de dados $DB_NAME"
fi
