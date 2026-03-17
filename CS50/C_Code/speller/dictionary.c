// Implements a dictionary's functionality

#include <ctype.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <strings.h>

#include "dictionary.h"

// Represents a node in a hash table
typedef struct node
{
    char word[LENGTH];
    struct node *next;
} node;

// TODO: Choose number of buckets in hash table
const unsigned int N = 5000;

// Hash table
node *table[N];

//Counter for the size
unsigned int number_of_words = 0;

// Returns true if word is in dictionary, else false
bool check(const char *word)
{
    unsigned int bucket = hash(word);
    node *n = table[bucket];

    while (n != NULL)
    {
        if (strcasecmp(word, n->word) == 0)
        {
            return true;
        }
        else
        {
            n = n->next;
        }
    }

    return false;
}

// Hashes word to a number
unsigned int hash(const char *word)
{
    int counter = 0;
    unsigned int hash = 0;
    while (word[counter] != '\0')
    {
        hash = (hash * 919 + tolower(word[counter])) % N;
        counter++;
    }

    return hash%N;
}

// Loads dictionary into memory, returning true if successful, else false
bool load(const char *dictionary)
{
    FILE *file = fopen(dictionary, "r");
    if (file == NULL)
    {
        printf("Could not open file\n");
        return 1;
    }

    char buffer[LENGTH + 1];
    while (fgets(buffer, LENGTH + 1, file))
    {
        buffer[strcspn(buffer, "\n")] = '\0';
        unsigned int bucket = hash(buffer);
        node *n = malloc(sizeof(node));
        if (n == NULL)
        {
            free(n);
            return 1;
        }

        strcpy(n->word, buffer);
        number_of_words++;
        if (table[bucket] == NULL)
        {
            n->next = NULL;
            table[bucket] = n;
        }
        else
        {
            n->next = table[bucket];
            table[bucket] = n;
        }
    }

    fclose(file);

    return true;
}

// Returns number of words in dictionary if loaded, else 0 if not yet loaded
unsigned int size(void)
{
    return number_of_words;
}

// Unloads dictionary from memory, returning true if successful, else false
bool unload(void)
{
    for (int i = 0; i < N; i++)
    {
        node *tmp = table[i];
        while (tmp != NULL)
        {
            node *next = tmp->next;
            free(tmp);
            tmp = next;
        }
    }
    return true;
}
