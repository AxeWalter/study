#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

const int FAT_size = 512;

int main(int argc, char *argv[])
{
    if (argc != 2)
    {
        printf("Too many arguments. Expected: 1.");
        return 1;
    }

    FILE *card = fopen(argv[1], "r");
    if (card == NULL)
    {
        printf("Unable to open file");
        return 1;
    }

    uint8_t buffer[FAT_size];

    int counter = 0;
    bool first_jpg = true;
    FILE *image = NULL;
    while (fread(buffer, 1, FAT_size, card) == 512)
    {
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff &&
            (buffer[3] & 0xf0) == 0xe0)
        {
            char filename[12];
            sprintf(filename, "%03i.jpg", counter);

            if (first_jpg == true)
            {
                image = fopen(filename, "w");
                first_jpg = false;
            }
            else
            {
                fclose(image);
                image = fopen(filename, "w");
            }

            if (image == NULL)
            {
                printf("Error creating file %s\n", filename);
                return 1;
            }
            fwrite(buffer, 1, FAT_size, image);
            counter++;
        }

        else if (image != NULL)
        {
            fwrite(buffer, 1, FAT_size, image);
        }
    }
    fclose(image);
    fclose(card);
    return 0;
}
