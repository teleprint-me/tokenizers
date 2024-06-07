"""
Module: tok.gguf.cli.unicode

Generate 'unicode-data.cpp' and 'unicode-data.h'
"""

import argparse
import ctypes
import logging

from ..unicode import CodepointFlags, CodepointProcessor

logger = logging.getLogger(__file__)


def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate 'unicode-data.cpp' and 'unicode-data.h'"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Output generated source text (default: False)",
    )

    # output path - default to stdout if no output path is given
    parser.add_argument(
        "--output-path",
        type=str,
        help="Output file path (default: stdout)",
    )

    # endianess - default to little-endian if no option provided
    parser.add_argument(
        "--big-endian",
        action="store_true",
        help="The byte order of the code points (default: False ('little'))",
    )

    # max_codepoints - default to 0x110000 if no boundary is given
    parser.add_argument(
        "--max-codepoints",
        type=int,
        default=0x110000,
        help="Maximum code points limit (default: 0x110000)",
    )

    return parser.parse_args()


def build_unicode_data_h(max_codepoints: int = 0x110000) -> str:
    # NOTE: The resulting string is segmented to prevent formatting conflicts with braces
    return """
    #pragma once

    #include <cstdint>
    #include <vector>
    #include <unordered_map>
    #include <unordered_set>

    struct range_nfd {
        uint32_t first;
        uint32_t last;
        uint32_t nfd;
    };
    """
    f"""
    static const uint32_t MAX_CODEPOINTS = {max_codepoints};
    """
    """
    extern const std::vector<std::pair<uint32_t, uint16_t>> unicode_ranges_flags;
    extern const std::unordered_set<uint32_t> unicode_set_whitespace;
    extern const std::unordered_map<uint32_t, uint32_t> unicode_map_lowercase;
    extern const std::unordered_map<uint32_t, uint32_t> unicode_map_uppercase;
    extern const std::vector<range_nfd> unicode_ranges_nfd;
    """


# TODO: define helper functions for setting mapping?
def set_ranges_flags(processor: CodepointProcessor, byte_order: str = "little") -> str:
    unicode_ranges_flags = (
        "// start, flags // last=next_start-1\n"
        "const std::vector<std::pair<uint32_t, uint16_t>> unicode_ranges_flags = {"
    )
    logger.debug(unicode_ranges_flags)

    for codepoint, flags in processor.codepoint_ranges.flags:
        flags = int.from_bytes(bytes(flags), byte_order)
        line = "{0x%06X, 0x%04X}," % (codepoint, flags)
        logger.debug(line)
        unicode_ranges_flags += line

    line = "};\n"
    logger.debug(line)
    unicode_ranges_flags += line
    return unicode_ranges_flags


def set_unicode_whitespace(processor: CodepointProcessor) -> str:
    unicode_set_whitespace = (
        "const std::unordered_set<uint32_t> unicode_set_whitespace = {"
    )
    logger.debug(unicode_set_whitespace)

    for codepoint in processor.unicode_table.whitespace:
        line = ", ".join("0x%06X" % codepoint)
        logger.debug(line)
        unicode_set_whitespace += line

    line = "};\n"
    logger.debug(line)
    unicode_set_whitespace += line
    return unicode_set_whitespace


def set_unicode_lowercase(processor: CodepointProcessor) -> str:
    out("const std::unordered_map<uint32_t, uint32_t> unicode_map_lowercase = {")
    for tuple in processor.unicode_table.lowercase:
        out("{0x%06X, 0x%06X}," % tuple)
    out("};\n")


def set_unicode_uppercase(processor: CodepointProcessor) -> str:
    out("const std::unordered_map<uint32_t, uint32_t> unicode_map_uppercase = {")
    for tuple in processor.unicode_table.uppercase:
        out("{0x%06X, 0x%06X}," % tuple)
    out("};\n")


def set_ranges_nfd(processor: CodepointProcessor) -> str:
    out("const std::vector<range_nfd> unicode_ranges_nfd = {  // start, last, nfd")
    for triple in processor.codepoint_ranges.nfd:
        out("{0x%06X, 0x%06X, 0x%06X}," % triple)
    out("};\n")


def build_unicode_data_cpp(processor: CodepointProcessor) -> str:
    # define includes
    unicode_data_cpp = """
    // generated with python gguf.cli.unicode

    #include "unicode-data.h"

    #include <cstdint>
    #include <vector>
    #include <unordered_map>
    #include <unordered_set>
    """
    logger.debug(unicode_data_cpp)
    unicode_data_cpp += set_ranges_flags(processor)
    unicode_data_cpp += set_unicode_whitespace(processor)
    # set ranges flags
    # set whitespace
    # map lowercase
    # map uppercase
    # set ranges nfd
    return unicode_data_cpp


def main():
    assert ctypes.sizeof(CodepointFlags) == 2

    args = get_arguments()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    processor = CodepointProcessor(args.max_codepoints)
    processor.process_unicode()
    processor.group_flag_ranges()
    processor.group_nfd_ranges()

    # build the header file
    unicode_data_h = build_unicode_data_h(args.max_codepoints)

    # build the source file
    unicode_data_cpp = build_unicode_data_cpp(processor)

    def out(line=""):
        print(line, end="\n")  # noqa

    out(
        """\
    // generated with scripts/gen-unicode-data.py

    #include "unicode-data.h"

    #include <cstdint>
    #include <vector>
    #include <unordered_map>
    #include <unordered_set>
    """
    )

    out(
        "const std::vector<std::pair<uint32_t, uint16_t>> unicode_ranges_flags = {  // start, flags // last=next_start-1"
    )
    for codepoint, flags in processor.codepoint_ranges.flags:
        flags = int.from_bytes(bytes(flags), "little")
        out("{0x%06X, 0x%04X}," % (codepoint, flags))
    out("};\n")

    out("const std::unordered_set<uint32_t> unicode_set_whitespace = {")
    out(", ".join("0x%06X" % cpt for cpt in processor.unicode_table.whitespace))
    out("};\n")

    out("const std::unordered_map<uint32_t, uint32_t> unicode_map_lowercase = {")
    for tuple in processor.unicode_table.lowercase:
        out("{0x%06X, 0x%06X}," % tuple)
    out("};\n")

    out("const std::unordered_map<uint32_t, uint32_t> unicode_map_uppercase = {")
    for tuple in processor.unicode_table.uppercase:
        out("{0x%06X, 0x%06X}," % tuple)
    out("};\n")

    out("const std::vector<range_nfd> unicode_ranges_nfd = {  // start, last, nfd")
    for triple in processor.codepoint_ranges.nfd:
        out("{0x%06X, 0x%06X, 0x%06X}," % triple)
    out("};\n")


if __name__ == "__main__":
    main()
