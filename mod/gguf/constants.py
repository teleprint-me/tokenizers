from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum, IntEnum, auto
from pathlib import Path
from typing import Any, Optional

#
# constants
#
GGUF_MAGIC = 0x46554747  # "GGUF"
GGUF_VERSION = 3
GGUF_DEFAULT_ALIGNMENT = 32
GGML_QUANT_VERSION = 2  # GGML_QNT_VERSION from ggml.h


#
# model metadata keys
#
class GGUFMetadataKeys:
    class General:
        ARCHITECTURE = "general.architecture"
        QUANTIZATION_VERSION = "general.quantization_version"
        ALIGNMENT = "general.alignment"
        NAME = "general.name"
        BASENAME = "general.basename"
        FINETUNE = "general.finetune"
        AUTHOR = "general.author"
        ORGANIZATION = "general.organization"
        VERSION = "general.version"
        BASE_VERSION = "general.base_version"
        URL = "general.url"
        DESCRIPTION = "general.description"
        LICENSE = "general.license"
        LICENSE_NAME = "general.license.name"
        LICENSE_LINK = "general.license.link"
        SOURCE_URL = "general.source.url"
        SOURCE_REPO = "general.source.repository"
        FILE_TYPE = "general.file_type"
        PARAMETER_SIZE_CLASS = "general.parameter_size_class"
        TAGS = "general.tags"
        LANGUAGE = "general.language"
        DATASETS = "general.datasets"
        ENDIANESS = "general.endianess"  # little or big

    class LLM:
        VOCAB_SIZE = "{arch}.vocab_size"
        CONTEXT_LENGTH = "{arch}.context_length"
        EMBEDDING_LENGTH = "{arch}.embedding_length"
        BLOCK_COUNT = "{arch}.block_count"
        FEED_FORWARD_LENGTH = "{arch}.feed_forward_length"
        USE_PARALLEL_RESIDUAL = "{arch}.use_parallel_residual"
        TENSOR_DATA_LAYOUT = "{arch}.tensor_data_layout"
        EXPERT_COUNT = "{arch}.expert_count"
        EXPERT_USED_COUNT = "{arch}.expert_used_count"
        POOLING_TYPE = "{arch}.pooling_type"
        LOGIT_SCALE = "{arch}.logit_scale"

    class Attention:
        HEAD_COUNT = "{arch}.attention.head_count"
        HEAD_COUNT_KV = "{arch}.attention.head_count_kv"
        MAX_ALIBI_BIAS = "{arch}.attention.max_alibi_bias"
        CLAMP_KQV = "{arch}.attention.clamp_kqv"
        KEY_LENGTH = "{arch}.attention.key_length"
        VALUE_LENGTH = "{arch}.attention.value_length"
        LAYERNORM_EPS = "{arch}.attention.layer_norm_epsilon"
        LAYERNORM_RMS_EPS = "{arch}.attention.layer_norm_rms_epsilon"
        CAUSAL = "{arch}.attention.causal"

    class Rope:
        DIMENSION_COUNT = "{arch}.rope.dimension_count"
        FREQ_BASE = "{arch}.rope.freq_base"
        SCALING_TYPE = "{arch}.rope.scaling.type"
        SCALING_FACTOR = "{arch}.rope.scaling.factor"
        SCALING_ATTN_FACTOR = "{arch}.rope.scaling.attn_factor"
        SCALING_ORIG_CTX_LEN = "{arch}.rope.scaling.original_context_length"
        SCALING_FINETUNED = "{arch}.rope.scaling.finetuned"

    class SSM:
        CONV_KERNEL = "{arch}.ssm.conv_kernel"
        INNER_SIZE = "{arch}.ssm.inner_size"
        STATE_SIZE = "{arch}.ssm.state_size"
        TIME_STEP_RANK = "{arch}.ssm.time_step_rank"

    class Tokenizer:
        MODEL = "tokenizer.model"  # STRING: e.g. llama, gpt2, etc...
        TYPE = "tokenizer.type"  # STRING: BPE, SPM, WPM, etc.
        NORM = "tokenizer.norm"  # OBJECT {"type": "ByteLevel", ...}
        PRE = "tokenizer.pre"  # OBJECT {"type": "ByteLevel", ...}
        ADDED = "tokenizer.added"  # ARRAY of OBJECTs: [{"id": 1, ...}, ...]
        VOCAB = "tokenizer.vocab"  # ARRAY of STRINGs: ["[BOS]", ...]
        MERGES = "tokenizer.merges"  # ARRAY of STRINGs: ["▁ t", ...]
        TOKEN_TYPE = "tokenizer.token_type"  # ARRAY of INT [2, ...]
        TOKEN_TYPE_COUNT = "tokenizer.token_type_count"  # BERT token types
        SCORES = "tokenizer.scores"  # WPM only
        BOS_ID = "tokenizer.bos_token_id"
        EOS_ID = "tokenizer.eos_token_id"
        UNK_ID = "tokenizer.unknown_token_id"
        SEP_ID = "tokenizer.separator_token_id"
        PAD_ID = "tokenizer.padding_token_id"
        CLS_ID = "tokenizer.cls_token_id"
        MASK_ID = "tokenizer.mask_token_id"
        ADD_BOS = "tokenizer.add_bos_token"
        ADD_EOS = "tokenizer.add_eos_token"
        ADD_PREFIX = "tokenizer.add_space_prefix"
        RWKV = "tokenizer.rwkv.world"
        CHAT_TEMPLATE = "tokenizer.chat_template"
        CHAT_TEMPLATE_N = "tokenizer.chat_template.{name}"
        CHAT_TEMPLATES = "tokenizer.chat_templates"
        # FIM/Infill special tokens constants
        PREFIX_ID = "tokenizer.prefix_token_id"
        SUFFIX_ID = "tokenizer.suffix_token_id"
        MIDDLE_ID = "tokenizer.middle_token_id"
        EOT_ID = "tokenizer.eot_token_id"


#
# recommended mapping of model tensor names for storage in gguf
#


class GGUF_MODEL_ARCH(IntEnum):
    LLAMA = auto()
    FALCON = auto()
    BAICHUAN = auto()
    GROK = auto()
    GPT2 = auto()
    GPTJ = auto()
    GPTNEOX = auto()
    MPT = auto()
    STARCODER = auto()
    REFACT = auto()
    BERT = auto()
    NOMIC_BERT = auto()
    JINA_BERT_V2 = auto()
    BLOOM = auto()
    STABLELM = auto()
    QWEN = auto()
    QWEN2 = auto()
    QWEN2MOE = auto()
    PHI2 = auto()
    PHI3 = auto()
    PLAMO = auto()
    CODESHELL = auto()
    ORION = auto()
    INTERNLM2 = auto()
    MINICPM = auto()
    GEMMA = auto()
    STARCODER2 = auto()
    MAMBA = auto()
    XVERSE = auto()
    COMMAND_R = auto()
    DBRX = auto()
    OLMO = auto()
    ARCTIC = auto()


class GGUF_MODEL_TENSOR(IntEnum):
    TOKEN_EMBD = auto()
    TOKEN_EMBD_NORM = auto()
    TOKEN_TYPES = auto()
    POS_EMBD = auto()
    OUTPUT = auto()
    OUTPUT_NORM = auto()
    ROPE_FREQS = auto()
    ROPE_FACTORS_LONG = auto()
    ROPE_FACTORS_SHORT = auto()
    ATTN_Q = auto()
    ATTN_K = auto()
    ATTN_V = auto()
    ATTN_QKV = auto()
    ATTN_OUT = auto()
    ATTN_NORM = auto()
    ATTN_NORM_2 = auto()
    ATTN_OUT_NORM = auto()
    ATTN_ROT_EMBD = auto()
    FFN_GATE_INP = auto()
    FFN_GATE_INP_SHEXP = auto()
    FFN_NORM = auto()
    FFN_GATE = auto()
    FFN_DOWN = auto()
    FFN_UP = auto()
    FFN_ACT = auto()
    FFN_NORM_EXP = auto()
    FFN_GATE_EXP = auto()
    FFN_DOWN_EXP = auto()
    FFN_UP_EXP = auto()
    FFN_GATE_SHEXP = auto()
    FFN_DOWN_SHEXP = auto()
    FFN_UP_SHEXP = auto()
    ATTN_Q_NORM = auto()
    ATTN_K_NORM = auto()
    LAYER_OUT_NORM = auto()
    SSM_IN = auto()
    SSM_CONV1D = auto()
    SSM_X = auto()
    SSM_DT = auto()
    SSM_A = auto()
    SSM_D = auto()
    SSM_OUT = auto()


GGUF_MODEL_ARCH_NAMES: dict[GGUF_MODEL_ARCH, str] = {
    GGUF_MODEL_ARCH.LLAMA: "llama",
    GGUF_MODEL_ARCH.FALCON: "falcon",
    GGUF_MODEL_ARCH.BAICHUAN: "baichuan",
    GGUF_MODEL_ARCH.GROK: "grok",
    GGUF_MODEL_ARCH.GPT2: "gpt2",
    GGUF_MODEL_ARCH.GPTJ: "gptj",
    GGUF_MODEL_ARCH.GPTNEOX: "gptneox",
    GGUF_MODEL_ARCH.MPT: "mpt",
    GGUF_MODEL_ARCH.STARCODER: "starcoder",
    GGUF_MODEL_ARCH.REFACT: "refact",
    GGUF_MODEL_ARCH.BERT: "bert",
    GGUF_MODEL_ARCH.NOMIC_BERT: "nomic-bert",
    GGUF_MODEL_ARCH.JINA_BERT_V2: "jina-bert-v2",
    GGUF_MODEL_ARCH.BLOOM: "bloom",
    GGUF_MODEL_ARCH.STABLELM: "stablelm",
    GGUF_MODEL_ARCH.QWEN: "qwen",
    GGUF_MODEL_ARCH.QWEN2: "qwen2",
    GGUF_MODEL_ARCH.QWEN2MOE: "qwen2moe",
    GGUF_MODEL_ARCH.PHI2: "phi2",
    GGUF_MODEL_ARCH.PHI3: "phi3",
    GGUF_MODEL_ARCH.PLAMO: "plamo",
    GGUF_MODEL_ARCH.CODESHELL: "codeshell",
    GGUF_MODEL_ARCH.ORION: "orion",
    GGUF_MODEL_ARCH.INTERNLM2: "internlm2",
    GGUF_MODEL_ARCH.MINICPM: "minicpm",
    GGUF_MODEL_ARCH.GEMMA: "gemma",
    GGUF_MODEL_ARCH.STARCODER2: "starcoder2",
    GGUF_MODEL_ARCH.MAMBA: "mamba",
    GGUF_MODEL_ARCH.XVERSE: "xverse",
    GGUF_MODEL_ARCH.COMMAND_R: "command-r",
    GGUF_MODEL_ARCH.DBRX: "dbrx",
    GGUF_MODEL_ARCH.OLMO: "olmo",
    GGUF_MODEL_ARCH.ARCTIC: "arctic",
}

GGUF_TENSOR_NAMES: dict[GGUF_MODEL_TENSOR, str] = {
    GGUF_MODEL_TENSOR.TOKEN_EMBD: "token_embd",
    GGUF_MODEL_TENSOR.TOKEN_EMBD_NORM: "token_embd_norm",
    GGUF_MODEL_TENSOR.TOKEN_TYPES: "token_types",
    GGUF_MODEL_TENSOR.POS_EMBD: "position_embd",
    GGUF_MODEL_TENSOR.OUTPUT_NORM: "output_norm",
    GGUF_MODEL_TENSOR.OUTPUT: "output",
    GGUF_MODEL_TENSOR.ROPE_FREQS: "rope_freqs",
    GGUF_MODEL_TENSOR.ROPE_FACTORS_LONG: "rope_factors_long",
    GGUF_MODEL_TENSOR.ROPE_FACTORS_SHORT: "rope_factors_short",
    GGUF_MODEL_TENSOR.ATTN_NORM: "blk.{bid}.attn_norm",
    GGUF_MODEL_TENSOR.ATTN_NORM_2: "blk.{bid}.attn_norm_2",
    GGUF_MODEL_TENSOR.ATTN_QKV: "blk.{bid}.attn_qkv",
    GGUF_MODEL_TENSOR.ATTN_Q: "blk.{bid}.attn_q",
    GGUF_MODEL_TENSOR.ATTN_K: "blk.{bid}.attn_k",
    GGUF_MODEL_TENSOR.ATTN_V: "blk.{bid}.attn_v",
    GGUF_MODEL_TENSOR.ATTN_OUT: "blk.{bid}.attn_output",
    GGUF_MODEL_TENSOR.ATTN_ROT_EMBD: "blk.{bid}.attn_rot_embd",
    GGUF_MODEL_TENSOR.ATTN_Q_NORM: "blk.{bid}.attn_q_norm",
    GGUF_MODEL_TENSOR.ATTN_K_NORM: "blk.{bid}.attn_k_norm",
    GGUF_MODEL_TENSOR.ATTN_OUT_NORM: "blk.{bid}.attn_output_norm",
    GGUF_MODEL_TENSOR.FFN_GATE_INP: "blk.{bid}.ffn_gate_inp",
    GGUF_MODEL_TENSOR.FFN_GATE_INP_SHEXP: "blk.{bid}.ffn_gate_inp_shexp",
    GGUF_MODEL_TENSOR.FFN_NORM: "blk.{bid}.ffn_norm",
    GGUF_MODEL_TENSOR.FFN_GATE: "blk.{bid}.ffn_gate",
    GGUF_MODEL_TENSOR.FFN_DOWN: "blk.{bid}.ffn_down",
    GGUF_MODEL_TENSOR.FFN_UP: "blk.{bid}.ffn_up",
    GGUF_MODEL_TENSOR.FFN_GATE_SHEXP: "blk.{bid}.ffn_gate_shexp",
    GGUF_MODEL_TENSOR.FFN_DOWN_SHEXP: "blk.{bid}.ffn_down_shexp",
    GGUF_MODEL_TENSOR.FFN_UP_SHEXP: "blk.{bid}.ffn_up_shexp",
    GGUF_MODEL_TENSOR.FFN_ACT: "blk.{bid}.ffn",
    GGUF_MODEL_TENSOR.FFN_NORM_EXP: "blk.{bid}.ffn_norm_exps",
    GGUF_MODEL_TENSOR.FFN_GATE_EXP: "blk.{bid}.ffn_gate_exps",
    GGUF_MODEL_TENSOR.FFN_DOWN_EXP: "blk.{bid}.ffn_down_exps",
    GGUF_MODEL_TENSOR.FFN_UP_EXP: "blk.{bid}.ffn_up_exps",
    GGUF_MODEL_TENSOR.LAYER_OUT_NORM: "blk.{bid}.layer_output_norm",
    GGUF_MODEL_TENSOR.SSM_IN: "blk.{bid}.ssm_in",
    GGUF_MODEL_TENSOR.SSM_CONV1D: "blk.{bid}.ssm_conv1d",
    GGUF_MODEL_TENSOR.SSM_X: "blk.{bid}.ssm_x",
    GGUF_MODEL_TENSOR.SSM_DT: "blk.{bid}.ssm_dt",
    GGUF_MODEL_TENSOR.SSM_A: "blk.{bid}.ssm_a",
    GGUF_MODEL_TENSOR.SSM_D: "blk.{bid}.ssm_d",
    GGUF_MODEL_TENSOR.SSM_OUT: "blk.{bid}.ssm_out",
}

GGUF_MODEL_TENSORS: dict[GGUF_MODEL_ARCH, list[GGUF_MODEL_TENSOR]] = {
    GGUF_MODEL_ARCH.LLAMA: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ROPE_FREQS,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
        GGUF_MODEL_TENSOR.FFN_GATE_INP,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_GATE,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
        GGUF_MODEL_TENSOR.FFN_GATE_EXP,
        GGUF_MODEL_TENSOR.FFN_DOWN_EXP,
        GGUF_MODEL_TENSOR.FFN_UP_EXP,
    ],
    GGUF_MODEL_ARCH.GROK: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ROPE_FREQS,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
        GGUF_MODEL_TENSOR.ATTN_OUT_NORM,
        GGUF_MODEL_TENSOR.FFN_GATE_INP,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_GATE,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
        GGUF_MODEL_TENSOR.FFN_GATE_EXP,
        GGUF_MODEL_TENSOR.FFN_DOWN_EXP,
        GGUF_MODEL_TENSOR.FFN_UP_EXP,
        GGUF_MODEL_TENSOR.LAYER_OUT_NORM,
    ],
    GGUF_MODEL_ARCH.GPTNEOX: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_QKV,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.FALCON: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_NORM_2,
        GGUF_MODEL_TENSOR.ATTN_QKV,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.BAICHUAN: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ROPE_FREQS,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_GATE,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.STARCODER: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.POS_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_QKV,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.BERT: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.TOKEN_EMBD_NORM,
        GGUF_MODEL_TENSOR.TOKEN_TYPES,
        GGUF_MODEL_TENSOR.POS_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.ATTN_OUT_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
        GGUF_MODEL_TENSOR.LAYER_OUT_NORM,
    ],
    GGUF_MODEL_ARCH.NOMIC_BERT: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.TOKEN_EMBD_NORM,
        GGUF_MODEL_TENSOR.TOKEN_TYPES,
        GGUF_MODEL_TENSOR.POS_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.ATTN_OUT_NORM,
        GGUF_MODEL_TENSOR.ATTN_QKV,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_GATE,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
        GGUF_MODEL_TENSOR.LAYER_OUT_NORM,
    ],
    GGUF_MODEL_ARCH.JINA_BERT_V2: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.TOKEN_EMBD_NORM,
        GGUF_MODEL_TENSOR.TOKEN_TYPES,
        GGUF_MODEL_TENSOR.ATTN_OUT_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_Q_NORM,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_K_NORM,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_UP,
        GGUF_MODEL_TENSOR.FFN_GATE,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.LAYER_OUT_NORM,
    ],
    GGUF_MODEL_ARCH.MPT: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_QKV,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
        GGUF_MODEL_TENSOR.FFN_ACT,
        GGUF_MODEL_TENSOR.ATTN_Q_NORM,
        GGUF_MODEL_TENSOR.ATTN_K_NORM,
        GGUF_MODEL_TENSOR.POS_EMBD,
    ],
    GGUF_MODEL_ARCH.GPTJ: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.REFACT: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_GATE,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.BLOOM: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.TOKEN_EMBD_NORM,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_QKV,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.STABLELM: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ROPE_FREQS,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_GATE,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
        GGUF_MODEL_TENSOR.ATTN_Q_NORM,
        GGUF_MODEL_TENSOR.ATTN_K_NORM,
    ],
    GGUF_MODEL_ARCH.QWEN: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ROPE_FREQS,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_QKV,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_GATE,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.QWEN2: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_GATE,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.QWEN2MOE: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_GATE_INP,
        GGUF_MODEL_TENSOR.FFN_GATE_EXP,
        GGUF_MODEL_TENSOR.FFN_DOWN_EXP,
        GGUF_MODEL_TENSOR.FFN_UP_EXP,
        GGUF_MODEL_TENSOR.FFN_GATE_INP_SHEXP,
        GGUF_MODEL_TENSOR.FFN_GATE_SHEXP,
        GGUF_MODEL_TENSOR.FFN_DOWN_SHEXP,
        GGUF_MODEL_TENSOR.FFN_UP_SHEXP,
    ],
    GGUF_MODEL_ARCH.PLAMO: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ROPE_FREQS,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
        GGUF_MODEL_TENSOR.FFN_GATE,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.GPT2: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.POS_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_QKV,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.PHI2: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_QKV,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.PHI3: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_QKV,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.CODESHELL: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.POS_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_QKV,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.ORION: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ROPE_FREQS,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_GATE,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.INTERNLM2: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_GATE,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.MINICPM: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.ROPE_FREQS,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
        GGUF_MODEL_TENSOR.FFN_GATE_INP,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_GATE,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
        GGUF_MODEL_TENSOR.FFN_GATE_EXP,
        GGUF_MODEL_TENSOR.FFN_DOWN_EXP,
        GGUF_MODEL_TENSOR.FFN_UP_EXP,
    ],
    GGUF_MODEL_ARCH.GEMMA: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_GATE,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
        GGUF_MODEL_TENSOR.FFN_NORM,
    ],
    GGUF_MODEL_ARCH.STARCODER2: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ROPE_FREQS,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.MAMBA: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.SSM_IN,
        GGUF_MODEL_TENSOR.SSM_CONV1D,
        GGUF_MODEL_TENSOR.SSM_X,
        GGUF_MODEL_TENSOR.SSM_DT,
        GGUF_MODEL_TENSOR.SSM_A,
        GGUF_MODEL_TENSOR.SSM_D,
        GGUF_MODEL_TENSOR.SSM_OUT,
    ],
    GGUF_MODEL_ARCH.XVERSE: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ROPE_FREQS,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_GATE,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.COMMAND_R: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_GATE,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
        GGUF_MODEL_TENSOR.ATTN_K_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q_NORM,
    ],
    GGUF_MODEL_ARCH.DBRX: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_QKV,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.ATTN_OUT_NORM,
        GGUF_MODEL_TENSOR.FFN_GATE_INP,
        GGUF_MODEL_TENSOR.FFN_GATE_EXP,
        GGUF_MODEL_TENSOR.FFN_DOWN_EXP,
        GGUF_MODEL_TENSOR.FFN_UP_EXP,
    ],
    GGUF_MODEL_ARCH.OLMO: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.FFN_GATE,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
    ],
    GGUF_MODEL_ARCH.ARCTIC: [
        GGUF_MODEL_TENSOR.TOKEN_EMBD,
        GGUF_MODEL_TENSOR.OUTPUT_NORM,
        GGUF_MODEL_TENSOR.OUTPUT,
        GGUF_MODEL_TENSOR.ROPE_FREQS,
        GGUF_MODEL_TENSOR.ATTN_NORM,
        GGUF_MODEL_TENSOR.ATTN_Q,
        GGUF_MODEL_TENSOR.ATTN_K,
        GGUF_MODEL_TENSOR.ATTN_V,
        GGUF_MODEL_TENSOR.ATTN_OUT,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
        GGUF_MODEL_TENSOR.FFN_GATE_INP,
        GGUF_MODEL_TENSOR.FFN_NORM,
        GGUF_MODEL_TENSOR.FFN_GATE,
        GGUF_MODEL_TENSOR.FFN_DOWN,
        GGUF_MODEL_TENSOR.FFN_UP,
        GGUF_MODEL_TENSOR.FFN_NORM_EXP,
        GGUF_MODEL_TENSOR.FFN_GATE_EXP,
        GGUF_MODEL_TENSOR.FFN_DOWN_EXP,
        GGUF_MODEL_TENSOR.FFN_UP_EXP,
    ],
    # TODO
}

# tensors that will not be serialized
GGUF_MODEL_TENSOR_SKIP: dict[GGUF_MODEL_ARCH, list[GGUF_MODEL_TENSOR]] = {
    GGUF_MODEL_ARCH.LLAMA: [
        GGUF_MODEL_TENSOR.ROPE_FREQS,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
    ],
    GGUF_MODEL_ARCH.BAICHUAN: [
        GGUF_MODEL_TENSOR.ROPE_FREQS,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
    ],
    GGUF_MODEL_ARCH.QWEN: [
        GGUF_MODEL_TENSOR.ROPE_FREQS,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
    ],
    GGUF_MODEL_ARCH.CODESHELL: [
        GGUF_MODEL_TENSOR.ROPE_FREQS,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
    ],
    GGUF_MODEL_ARCH.ORION: [
        GGUF_MODEL_TENSOR.ROPE_FREQS,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
    ],
    GGUF_MODEL_ARCH.STARCODER2: [
        GGUF_MODEL_TENSOR.ROPE_FREQS,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
    ],
    GGUF_MODEL_ARCH.XVERSE: [
        GGUF_MODEL_TENSOR.ROPE_FREQS,
        GGUF_MODEL_TENSOR.ATTN_ROT_EMBD,
    ],
}


#
# types
#
class GGUFRopeScalingType(Enum):
    NONE = "none"
    LINEAR = "linear"
    YARN = "yarn"


class GGUFPoolingType(IntEnum):
    NONE = 0
    MEAN = 1
    CLS = 2


class GGUFQuantizationType(IntEnum):
    F32 = 0
    F16 = 1
    Q4_0 = 2
    Q4_1 = 3
    Q5_0 = 6
    Q5_1 = 7
    Q8_0 = 8
    Q8_1 = 9
    Q2_K = 10
    Q3_K = 11
    Q4_K = 12
    Q5_K = 13
    Q6_K = 14
    Q8_K = 15
    IQ2_XXS = 16
    IQ2_XS = 17
    IQ3_XXS = 18
    IQ1_S = 19
    IQ4_NL = 20
    IQ3_S = 21
    IQ2_S = 22
    IQ4_XS = 23
    I8 = 24
    I16 = 25
    I32 = 26
    I64 = 27
    F64 = 28
    IQ1_M = 29
    BF16 = 30


# TODO: add GGMLFileType from ggml_ftype in ggml.h


# from llama_ftype in llama.h
# ALL VALUES SHOULD BE THE SAME HERE AS THEY ARE OVER THERE.
class GGUFFileType(IntEnum):
    ALL_F32 = 0
    MOSTLY_F16 = 1  # except 1d tensors
    MOSTLY_Q4_0 = 2  # except 1d tensors
    MOSTLY_Q4_1 = 3  # except 1d tensors
    MOSTLY_Q4_1_SOME_F16 = 4  # tok_embeddings.weight and output.weight are F16
    # MOSTLY_Q4_2        = 5   # support has been removed
    # MOSTLY_Q4_3        = 6   # support has been removed
    MOSTLY_Q8_0 = 7  # except 1d tensors
    MOSTLY_Q5_0 = 8  # except 1d tensors
    MOSTLY_Q5_1 = 9  # except 1d tensors
    MOSTLY_Q2_K = 10  # except 1d tensors
    MOSTLY_Q3_K_S = 11  # except 1d tensors
    MOSTLY_Q3_K_M = 12  # except 1d tensors
    MOSTLY_Q3_K_L = 13  # except 1d tensors
    MOSTLY_Q4_K_S = 14  # except 1d tensors
    MOSTLY_Q4_K_M = 15  # except 1d tensors
    MOSTLY_Q5_K_S = 16  # except 1d tensors
    MOSTLY_Q5_K_M = 17  # except 1d tensors
    MOSTLY_Q6_K = 18  # except 1d tensors
    MOSTLY_IQ2_XXS = 19  # except 1d tensors
    MOSTLY_IQ2_XS = 20  # except 1d tensors
    MOSTLY_Q2_K_S = 21  # except 1d tensors
    MOSTLY_IQ3_XS = 22  # except 1d tensors
    MOSTLY_IQ3_XXS = 23  # except 1d tensors
    MOSTLY_IQ1_S = 24  # except 1d tensors
    MOSTLY_IQ4_NL = 25  # except 1d tensors
    MOSTLY_IQ3_S = 26  # except 1d tensors
    MOSTLY_IQ3_M = 27  # except 1d tensors
    MOSTLY_IQ2_S = 28  # except 1d tensors
    MOSTLY_IQ2_M = 29  # except 1d tensors
    MOSTLY_IQ4_XS = 30  # except 1d tensors
    MOSTLY_IQ1_M = 31  # except 1d tensors
    MOSTLY_BF16 = 32  # except 1d tensors

    GUESSED = 1024  # not specified in the model file


GGUF_FILE_TYPE_MAP = {
    "F32": GGUFFileType.ALL_F32,
    "F16": GGUFFileType.MOSTLY_F16,
    "BF16": GGUFFileType.MOSTLY_BF16,
    "Q8_0": GGUFFileType.MOSTLY_Q8_0,
}


GGUF_FILE_TYPE_NAMES: dict[GGUFFileType, str] = {
    GGUFFileType.ALL_F32: "F32",
    GGUFFileType.MOSTLY_F16: "F16",
    GGUFFileType.MOSTLY_BF16: "BF16",
    GGUFFileType.MOSTLY_Q8_0: "Q8_0",
}


class GGUFEndian(IntEnum):
    LITTLE = 0
    BIG = 1


class GGUFValueType(IntEnum):
    UINT8 = auto()
    INT8 = auto()
    UINT16 = auto()
    INT16 = auto()
    UINT32 = auto()
    INT32 = auto()
    UINT64 = auto()
    INT64 = auto()
    FLOAT32 = auto()
    FLOAT64 = auto()
    BOOL = auto()
    STRING = auto()
    ARRAY = auto()
    OBJECT = auto()

    @staticmethod
    def get_type(val: Any) -> GGUFValueType:
        if isinstance(val, (str, bytes, bytearray)):
            return GGUFValueType.STRING

        elif isinstance(val, bool):
            return GGUFValueType.BOOL

        # TODO: Need help with 64-bit types in Python.
        # NOTE: Maybe use numpy, e.g. np.dtypes to determine data type?
        # Using base types is unreliable in python as all numbers in python are 64-bits.
        # This is a non-trivial problem and will require a "clever" procedure.

        # If it's an integer (either signed or unsigned)
        if isinstance(val, int):
            return GGUFValueType.INT32

        elif isinstance(val, float):
            # NOTE: This is unreliable in python as all numbers in python are 64-bits
            return GGUFValueType.FLOAT32

        elif isinstance(val, list):
            return GGUFValueType.ARRAY

        elif isinstance(val, dict):
            # NOTE: JSON Object, Dict, or Mapping are valid types
            return GGUFValueType.OBJECT

        else:
            raise ValueError(f"Unknown type: {type(val)}")


# Items here are (block size, type size)
QK_K = 256
GGUF_QUANT_SIZES: dict[GGUFQuantizationType, tuple[int, int]] = {
    GGUFQuantizationType.F32: (1, 4),
    GGUFQuantizationType.F16: (1, 2),
    GGUFQuantizationType.Q4_0: (32, 2 + 16),
    GGUFQuantizationType.Q4_1: (32, 2 + 2 + 16),
    GGUFQuantizationType.Q5_0: (32, 2 + 4 + 16),
    GGUFQuantizationType.Q5_1: (32, 2 + 2 + 4 + 16),
    GGUFQuantizationType.Q8_0: (32, 2 + 32),
    GGUFQuantizationType.Q8_1: (32, 4 + 4 + 32),
    GGUFQuantizationType.Q2_K: (256, 2 + 2 + QK_K // 16 + QK_K // 4),
    GGUFQuantizationType.Q3_K: (256, 2 + QK_K // 4 + QK_K // 8 + 12),
    GGUFQuantizationType.Q4_K: (256, 2 + 2 + QK_K // 2 + 12),
    GGUFQuantizationType.Q5_K: (256, 2 + 2 + QK_K // 2 + QK_K // 8 + 12),
    GGUFQuantizationType.Q6_K: (256, 2 + QK_K // 2 + QK_K // 4 + QK_K // 16),
    GGUFQuantizationType.Q8_K: (256, 4 + QK_K + QK_K // 8),
    GGUFQuantizationType.IQ2_XXS: (256, 2 + QK_K // 4),
    GGUFQuantizationType.IQ2_XS: (256, 2 + QK_K // 4 + QK_K // 32),
    GGUFQuantizationType.IQ3_XXS: (256, 2 + QK_K // 4 + QK_K // 8),
    GGUFQuantizationType.IQ1_S: (256, 2 + QK_K // 8 + QK_K // 16),
    GGUFQuantizationType.IQ4_NL: (32, 2 + 16),
    GGUFQuantizationType.IQ3_S: (256, 2 + QK_K // 4 + QK_K // 8 + QK_K // 32 + 4),
    GGUFQuantizationType.IQ2_S: (256, 2 + QK_K // 4 + QK_K // 16),
    GGUFQuantizationType.IQ4_XS: (256, 2 + 2 + QK_K // 2 + QK_K // 64),
    GGUFQuantizationType.I8: (1, 1),
    GGUFQuantizationType.I16: (1, 2),
    GGUFQuantizationType.I32: (1, 4),
    GGUFQuantizationType.I64: (1, 8),
    GGUFQuantizationType.F64: (1, 8),
    GGUFQuantizationType.IQ1_M: (256, QK_K // 8 + QK_K // 16 + QK_K // 32),
    GGUFQuantizationType.BF16: (1, 2),
}


#
# Model File Types
#
class ModelFileExtension(Enum):
    PT = ".pt"  # torch
    PTH = ".pth"  # torch
    BIN = ".bin"  # torch
    SAFETENSORS = ".safetensors"  # safetensors
    JSON = ".json"  # transformers/tokenizers
    MODEL = ".model"  # sentencepiece
    GGUF = ".gguf"  # ggml/llama.cpp


#
# Tokenizer Types
#
class GGUFTokenType(IntEnum):
    NORMAL = 1
    UNKNOWN = 2
    CONTROL = 3
    USER_DEFINED = 4
    UNUSED = 5
    BYTE = 6


class HFTokenizerType(Enum):
    SPM = "SPM"  # SentencePiece LLaMa tokenizer
    BPE = "BPE"  # BytePair GPT-2 tokenizer
    WPM = "WPM"  # WordPiece BERT tokenizer


#
# Normalizer Types
#
class HFNormalizerType(Enum):
    SEQUENCE = "Sequence"
    NFC = "NFC"
    NFD = "NFD"
    NFKC = "NFKC"
    NFKD = "NFKD"


#
# Pre-tokenizer Types
#
class HFPreTokenizerType(Enum):
    WHITESPACE = "Whitespace"
    METASPACE = "Metaspace"
    BYTE_LEVEL = "ByteLevel"
    BERT_PRE_TOKENIZER = "BertPreTokenizer"
    SEQUENCE = "Sequence"


#
# HF Vocab Files
#
HF_TOKENIZER_BPE_FILES = (
    "config.json",
    "tokenizer_config.json",
    "tokenizer.json",
)

HF_TOKENIZER_SPM_FILES: tuple[str, ...] = HF_TOKENIZER_BPE_FILES + ("tokenizer.model",)
