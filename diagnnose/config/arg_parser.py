from argparse import ArgumentParser
from typing import Set, Tuple

from diagnnose.typedefs.config import ArgDescriptions


def create_arg_descriptions() -> ArgDescriptions:
    arg_descriptions: ArgDescriptions = {
        'model': {
            'model_type': {
                'required': True,
                'help': 'Language model type, as of now either '
                        'ForwardLSTM or GoogleLM.'
            }
        }
    }

    # Gulordava ForwardLSTM
    arg_descriptions['model'].update({
        'model_path': {
            'help': 'Path to model parameters'
        },
        'vocab_path': {
            'help': 'Path to model vocabulary'
        },
        'module_path': {
            'help': 'Path to folder containing model module'
        },
        'device': {
            'help': '(optional) Torch device name on which model will be run. Defaults to cpu.'
        },
    })

    # GoogleLM
    arg_descriptions['model'].update({
        'pbtxt_path': {
            'help': 'Path to the .pbtxt file containing the GraphDef model setup.'
        },
        'ckpt_dir': {
            'help': 'Path to folder containing parameter checkpoint files.'
        },
        'corpus_vocab_path': {
            'help': 'Path to the corpus vocabulary. This allows for only a subset of the model '
                    'softmax to be loaded in.'
        },
        'full_vocab_path': {
            'help': 'Path to the full model vocabulary of 800k tokens.'
        },
    })

    arg_descriptions['corpus'] = {
        'corpus_path': {
            'required': True,
            'help': 'Path to a corpus file.'
        },
        'corpus_header': {
            'nargs': '*',
            'help': '(optional) List of corpus attribute names. If not provided all lines will be '
                    'considered to be sentences, with the attribute name "sen".'
        },
        'to_lower': {
            'type': bool,
            'help': '(optional) Convert corpus to lowercase, defaults to False.'
        },
        'header_from_first_line': {
            'type': bool,
            'help': '(optional) Use the first line of the corpus as the attribute  names of the '
                    'corpus. Defaults to False.'
        },
    }

    arg_descriptions['activations'] = {
        # TODO: Provide explanation of activation names
        'activations_dir': {
            'required': True,
            'help': 'Path to folder to which extracted embeddings will be written.'
        },
        'init_lstm_states_path': {
            'help': '(optional) Location of initial lstm states of the model. '
                    'If no path is provided zero-initialized states will be used.'
        },
    }

    arg_descriptions['extract'] = {
        'activation_names': {
            'required': True,
            'nargs': '*',
            'help': 'List of activation names to be extracted.'
        },
        'dynamic_dumping': {
            'type': bool,
            'help': '(optional) Set to true to directly dump activations to file. '
                    'This way no activations are stored in RAM. Defaults to true.'
        },
        'create_label_file': {
            'type': bool,
            'help': '(optional) Set to true to directly store the corpus labels as a separate '
                    'numpy array. Defaults to True.'
        },
        'create_avg_eos': {
            'type': bool,
            'help': '(optional) Set to true to directly store the average end of sentence '
                    'activations. Defaults to False'
        },
        'print_every': {
            'type': int,
            'help': '(optional) Print extraction progress every n steps. Defaults to 20.'
        },
        'cutoff': {
            'type': int,
            'help': '(optional) Stop extraction after n sentences. Defaults to -1 to extract '
                    'entire corpus.'
        },
    }

    arg_descriptions['decompose'] = {
        'decomposer': {
            'required': True,
            'help': 'Class name of decomposer constructor. As of now either '
                    'CellDecomposer or ContextualDecomposer'
        }
    }

    return arg_descriptions


def create_arg_parser(arg_groups: Set[str]) -> Tuple[ArgumentParser, Set[str]]:
    parser = ArgumentParser()

    # create group to load config from a file
    from_config = parser.add_argument_group('From config file',
                                            'Provide full experiment setup via config json file.')
    from_config.add_argument('-c', '--config',
                             help='Path to json file containing extraction config.')

    # create group to provide info via commandline arguments
    # Required args are not set to be required here as they can come from --config
    from_cmd = parser.add_argument_group('From commandline',
                                         'Specify experiment setup via commandline arguments. '
                                         'Can be combined with the json config, in which case these'
                                         ' cmd arguments overwrite the config args.')

    arg_descriptions = create_arg_descriptions()
    required_args = set()
    for group in arg_groups:
        group_args = arg_descriptions[group]
        for arg, arg_config in group_args.items():
            from_cmd.add_argument(f'--{arg}',
                                  nargs=arg_config.get('nargs', None),
                                  type=arg_config.get('type', str),
                                  help=arg_config['help'])
            if arg_config.get('required', False):
                required_args.add(arg)

    return parser, required_args