# Photo Slideshow

```yml
services:
  photo-slider:
    image: ghcr.io/rossberi/photo-slider:latest
    container_name: photo-slider
    restart: unless-stopped
    ports:
      - 8100:8000
    volumes:
      - /home/$USER/docker/photo-slider:/app/static/images
    environment:
      - TZ=Europe/Berlin
      - SLIDESHOW_INTERVAL=10
networks: {}
```