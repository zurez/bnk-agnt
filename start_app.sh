#!/bin/bash

docker-compose down
docker-compose build #--no-cache
docker-compose up -d

sleep 5

echo -e "   • Frontend:     \033[4;34mhttp://localhost:3000\033[0m"
echo -e "   • Backend API:  \033[4;34mhttp://localhost:8000\033[0m"
echo -e "   • Phoenix UI:   \033[4;34mhttp://localhost:6006\033[0m"
echo -e "   • Database:     localhost:5432"
