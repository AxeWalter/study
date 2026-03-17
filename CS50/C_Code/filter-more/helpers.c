#include "helpers.h"
#include <math.h>
#define max(a, b) ((a) > (b) ? (a) : (b))
#define min(a, b) ((a) < (b) ? (a) : (b))

// Convert image to grayscale
void grayscale(int height, int width, RGBTRIPLE image[height][width])
{
    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int average = round(((float) image[i][j].rgbtBlue + (float) image[i][j].rgbtGreen +
                                 (float) image[i][j].rgbtRed) /
                                3);
            image[i][j].rgbtBlue = average;
            image[i][j].rgbtGreen = average;
            image[i][j].rgbtRed = average;
        }
    }
    return;
}

// Reflect image horizontally
void reflect(int height, int width, RGBTRIPLE image[height][width])
{

    RGBTRIPLE temp[width];
    for (int i = 0; i < height; i++)
    {
        for (int j = width - 1; j >= 0; j--)
        {
            temp[width - j - 1] = image[i][j];
        }
        for (int k = 0; k < width; k++)
        {
            image[i][k] = temp[k];
        }
    }
    return;
}

// Blur image. I'm gonna comment because this one is hard.
void blur(int height, int width, RGBTRIPLE image[height][width])
{
    // First of all, I initialize a temporary image with same height and width as our image. This is
    // necessary to hold the blured pixels without interfering in the final image.
    RGBTRIPLE temp[height][width];
    // We then procede to the normal nested loop to go through the 2d matrix.
    for (int i = 0; i < height; i++)
    {
        // The averages hold the value of the RGB colors around the pixel we selected. Division is
        // just an iteration counter to obtain the average. The slick part is this: i put this in
        // the loop so everytime we reset the selected pixel, the counter zeros :).
        for (int j = 0; j < width; j++)
        {
            int avg_red = 0;
            int avg_green = 0;
            int avg_blue = 0;
            int division = 0;

            // Here we start the weird, but easy part. To loop a 2d array we need a nested loop.
            // Well, we need to loop, max case, 3x3 around our pixel, so we need another nested
            // loop. The part that mr. duck helped me is with max and min. There's a catch with this
            // problem: edge pixel don't have a 3x3 matrix around it. These cases, it might be that
            // the line is 0 or the column. These way, we try the higher first: 0 or i - 1. Same to
            // stop the loop, but with the lower: 0 or i + 1. At last, why did i use i and j? Well,
            // i represents the line and j the column. This allows me to dinamically select the line
            // above, in and under our pixel. Same with the column.
            for (int k = (max(0, i - 1)); k <= min(i + 1, height - 1); k++)
            {
                for (int l = (max(0, j - 1)); l <= min(j + 1, width - 1); l++)
                {

                    // This is simply adding to our averages the values of R, B and G of each pixel
                    // around the selected pixel. Also, adding +1 to each loop, so we can get the
                    // average.
                    avg_red += image[k][l].rgbtRed;
                    avg_green += image[k][l].rgbtGreen;
                    avg_blue += image[k][l].rgbtBlue;
                    division++;
                }
            }
            // After getting all the values, we return to our pixel and calculate the averages. The
            // casting to float is so we don't lose any decimal values, and the rounding because RGB
            // are INT.
            avg_red = round((float) avg_red / division);
            avg_green = round((float) avg_green / division);
            avg_blue = round((float) avg_blue / division);
            // After getting the averages, we "create" our temp matrix with these values.
            temp[i][j].rgbtRed = avg_red;
            temp[i][j].rgbtGreen = avg_green;
            temp[i][j].rgbtBlue = avg_blue;
        }
    }

    // Did not find a way to do without a secondary loop. This will get all the values of temp and
    // put them blured in image.
    for (int a = 0; a < height; a++)
    {
        for (int b = 0; b < width; b++)
        {
            image[a][b] = temp[a][b];
        }
    }
    return;
}

// Detect edges
void edges(int height, int width, RGBTRIPLE image[height][width])
{
    int matrix_gx[3][3] = {{-1, 0, 1}, {-2, 0, 2}, {-1, 0, 1}};
    int matrix_gy[3][3] = {{-1, -2, -1}, {0, 0, 0}, {1, 2, 1}};

    RGBTRIPLE temp[height][width];

    for (int i = 0; i < height; i++)
    {
        for (int j = 0; j < width; j++)
        {
            int gx_red = 0;
            int gy_red = 0;
            int gx_green = 0;
            int gy_green = 0;
            int gx_blue = 0;
            int gy_blue = 0;

            for (int k = (max(0, i - 1)); k <= (min(i + 1, height - 1)); k++)
            {
                for (int l = (max(0, j - 1)); l <= (min(j + 1, width - 1)); l++)
                {
                    gx_red += image[k][l].rgbtRed * matrix_gx[i - k + 1][j - l + 1];
                    gy_red += image[k][l].rgbtRed * matrix_gy[i - k + 1][j - l + 1];
                    gx_green += image[k][l].rgbtGreen * matrix_gx[i - k + 1][j - l + 1];
                    gy_green += image[k][l].rgbtGreen * matrix_gy[i - k + 1][j - l + 1];
                    gx_blue += image[k][l].rgbtBlue * matrix_gx[i - k + 1][j - l + 1];
                    gy_blue += image[k][l].rgbtBlue * matrix_gy[i - k + 1][j - l + 1];
                }
            }

            int sobel_red = round(sqrt(((float) gx_red * gx_red) + ((float) gy_red * gy_red)));
            int sobel_green =
                round(sqrt(((float) gx_green * gx_green) + ((float) gy_green * gy_green)));
            int sobel_blue = round(sqrt(((float) gx_blue * gx_blue) + ((float) gy_blue * gy_blue)));
            (sobel_red <= 255) ? (temp[i][j].rgbtRed = sobel_red) : (temp[i][j].rgbtRed = 255);
            (sobel_green <= 255) ? (temp[i][j].rgbtGreen = sobel_green)
                                 : (temp[i][j].rgbtGreen = 255);
            (sobel_blue <= 255) ? (temp[i][j].rgbtBlue = sobel_blue) : (temp[i][j].rgbtBlue = 255);
        }
    }

    for (int a = 0; a < height; a++)
    {
        for (int b = 0; b < width; b++)
        {
            image[a][b] = temp[a][b];
        }
    }
    return;
}
