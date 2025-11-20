# AstroDX_ChartCat

Convert charts that is in legacy AstroDX storage structure into the new one.

_Why not use our [Rust version](https://github.com/Momoko-Ayase/AstroDX_ChartCat_rs)?_

## Usage

Put your data that is structured like this:

```plaintext
.
├───collection_name
│   ├───level_name
│   │       bg.jpg
│   │       maidata.txt
│   │       track.mp3
│   │
...
```

...into folder 'charts' beside the executable file (if not exists create one) and run the program.

Then you can put the generated 'collections' and 'levels' folders into the game data folder.

## Parameters

- `-novideo`: Do not copy video files. Will significantly reduce output size (better for devices with low storage).
- `-restore`: Restore the old storage structure.

## License

[MIT](LICENSE)
