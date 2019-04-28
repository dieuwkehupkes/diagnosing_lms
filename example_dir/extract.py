from argparse import ArgumentParser

from diagnnose.config.setup import ConfigSetup
from diagnnose.corpora.import_corpus import import_corpus_from_path
from diagnnose.extractors.base_extractor import Extractor
from diagnnose.models.import_model import import_model_from_json
from diagnnose.models.language_model import LanguageModel
from diagnnose.typedefs.corpus import Corpus


def init_argparser() -> ArgumentParser:
    parser = ArgumentParser()

    # create group to load config from a file
    from_config = parser.add_argument_group('From config file',
                                            'Provide full experiment setup via config file')
    from_config.add_argument('-c', '--config',
                             help='Path to json file containing extraction config.')

    # create group to provide info via commandline arguments
    # Required args are not set to be required here as they can come from --config
    from_cmd = parser.add_argument_group('From commandline',
                                         'Specify experiment setup via commandline arguments')
    from_cmd.add_argument('--model',
                          help='Path to model parameters')
    from_cmd.add_argument('--vocab',
                          help='Path to model vocabulary')
    from_cmd.add_argument('--lm_module',
                          help='Path to folder containing model module')
    from_cmd.add_argument('--corpus_path',
                          help='Path to labeled corpus')
    # TODO: Provide explanation of activation names
    from_cmd.add_argument('--activation_names',
                          help='Activations to be extracted', nargs='*')
    from_cmd.add_argument('--output_dir',
                          help='Path to folder to which extracted embeddings will be written.')
    from_cmd.add_argument('--corpus_header', nargs='*',
                          help='(optional) List of corpus attribute names.'
                               'If not provided first line is used as header.')
    from_cmd.add_argument('--to_lower', type=bool,
                          help='(optional) Convert corpus to lowercase, defaults to False.')
    from_cmd.add_argument('--from_dict', type=bool,
                          help='(optional) Set to true to load in pickled corpus dictionary, '
                               'instead of a raw file.')
    from_cmd.add_argument('--device',
                          help='(optional) Torch device name on which model will be run.'
                               'Defaults to cpu.')
    from_cmd.add_argument('--init_lstm_states_path',
                          help='(optional) Location of initial lstm states of the model. '
                               'If no path is provided zero-initialized states will be used at the'
                               'start of each sequence.')
    from_cmd.add_argument('--print_every', type=int,
                          help='(optional) Print extraction progress every n steps.'
                               'Defaults to 20.')
    from_cmd.add_argument('--cutoff', type=int,
                          help='(optional) Stop extraction after n sentences. '
                               'Defaults to -1 to extract entire corpus.')
    from_cmd.add_argument('--dynamic_dumping', type=bool,
                          help='(optional) Set to true to directly dump activations to file. '
                               'This way no activations are stored in RAM. Defaults to true.')
    from_cmd.add_argument('--create_label_file', type=bool,
                          help='(optional) Set to true to directly store the corpus labels as a '
                               'separate numpy array, defaults to True.')
    from_cmd.add_argument('--create_avg_eos', type=bool,
                          help='(optional) Set to true to directly store the average end of '
                               'sentence activations, defaults to False')

    return parser


if __name__ == '__main__':
    required_args = {'model', 'vocab', 'lm_module', 'corpus_path', 'activation_names', 'output_dir'}
    arg_groups = {
        'model': {'model', 'vocab', 'lm_module', 'device'},
        'corpus': {'corpus_path', 'corpus_header', 'to_lower', 'from_dict'},
        'init_extract': {'activation_names', 'output_dir', 'init_lstm_states_path'},
        'extract': {'cutoff', 'print_every', 'dynamic_dumping', 'create_label_file',
                    'create_avg_eos'},
    }
    argparser = init_argparser()

    config_object = ConfigSetup(argparser, required_args, arg_groups)
    config_dict = config_object.config_dict

    model: LanguageModel = import_model_from_json(**config_dict['model'])
    corpus: Corpus = import_corpus_from_path(**config_dict['corpus'])

    extractor = Extractor(model, corpus, **config_dict['init_extract'])
    extractor.extract(**config_dict['extract'])