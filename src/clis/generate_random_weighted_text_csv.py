import argparse
import csv
import random
import sys
from typing import Dict, List, TextIO
from itemcloud.cli_support.base import cli_helpers
from itemcloud.containers.named_text import NamedText
from itemcloud.util.fonts import pick_font
from itemcloud.containers.weighted_text import (
    WeightedText,
    WEIGHTED_TEXT_HEADERS,
    WEIGHTED_TEXT_CSV_FILE_HELP
)
from itemcloud.logger.base_logger import BaseLogger, set_logger_instance
from itemcloud.logger.file_logger import FileLogger

def arguments() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawTextHelpFormatter,
        prog='generate_weighted_text',
        description='''
        Generate randomly weighted text csv file from provided list of text arguments.
        {0}
        '''.format(WEIGHTED_TEXT_CSV_FILE_HELP)
    )
    parser.add_argument(
        '-c', 
        '--count',
        metavar='<total-words-randomly-picked>',
        type=int,
        required=True,
        help='''
        Required, Program will loop this many times, randomly picking 1 word from provided base array of text.
        Weights created are number of occurrences of each word in randomly generated list.
        '''
    )
    parser.add_argument(
        '--words',
        nargs='+',
        type=str,
        required=True,
        help='''
        Required, list of words|numbers|phrases (in quotes) making up base array of text.
        This array is iteratively randomly picked from to produce weighted word list.
        '''
    )
    parser.add_argument(
        '-output-filepath-csv',
        metavar='<output-filepath>',
        type=lambda fp: cli_helpers.existing_dirpath_of_filepath(parser, fp),
        help='Optional, weighted text csv filepath to create with output (default: stdout)'
    )
    parser.add_argument(
        '-log-filepath',
        metavar='<log-filepath>',
        type=lambda fp: cli_helpers.existing_dirpath_of_filepath(parser, fp),
        help='Optional, all output logging will also be written to this logfile'
        
    )
    return parser

def write_weighted_text(word_count_set: Dict[str,int], output_fd: TextIO) -> None:
    font = pick_font()
    csv_writer = csv.DictWriter(output_fd, fieldnames=WEIGHTED_TEXT_HEADERS)
    csv_writer.writeheader()
    for word, weight in word_count_set.items():
        csv_writer.writerow(WeightedText(float(weight), NamedText(word, word, font, None, None)).to_csv_row())

def generate_word_count_set(words: List[str], total_words: int) -> Dict[str, int]:
    result = {}
    random.seed()
    for _i in range(total_words):
        word = random.choice(words)
        if word in result:
            result[word] = 1 + result[word]
        else:
            result[word] = 1
    return result

def main() -> None:
    args = arguments().parse_args()
    if args.log_filepath:
        logger: BaseLogger = FileLogger.create('generate weighted text', False, args.log_filepath)
    else:
        logger: BaseLogger = BaseLogger.create('generate weighted text', False)
    set_logger_instance(logger)

    logger.info(f"Generate {args.count} random words from {len(args.words)} provided words.")
    word_count_set = generate_word_count_set(args.words, args.count)

    if args.output_filepath_csv:
        with open(args.output_filepath_csv, 'w') as fp:
            write_weighted_text(word_count_set, fp)
        logger.info(f"Wrote {args.count} words to {args.output_filepath_csv}")
    else:
        print(f"<CSV>")
        write_weighted_text(word_count_set, sys.stdout)
        print(f"</CSV>")

if __name__ == '__main__':
    main()