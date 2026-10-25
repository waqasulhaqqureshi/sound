New-Item -ItemType Directory -Force -Path ".\clips"; ffmpeg -i "input.mp4" -c copy -map 0 -segment_time 600 -f segment -reset_timestamps 1 ".\clips\part_%03d.mp4"
# sound