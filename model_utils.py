from keras.models import Model
from keras.layers import LSTM, Dense, Input, Dropout, Activation, Embedding
from keras.layers.wrappers import Bidirectional
from keras.callbacks import EarlyStopping
from keras.regularizers import l1_l2
import numpy as np


# val_f1_c
def get_callbacks(early_stop_monitor='val_acc', early_stop_patience=2, early_stop_mode='auto'):
    earlystop = EarlyStopping(monitor=early_stop_monitor, min_delta=0.001, patience=early_stop_patience, verbose=1, mode=early_stop_mode)

    return [earlystop]


def create_embedding_layer(embeddings_index, words_to_index, vocab_length=100, output_dim=300):
    emb_matrix = np.zeros((vocab_length + 1, output_dim))

    for word, index in words_to_index.items():
        if word in embeddings_index:
            emb_matrix[index, :] = embeddings_index[word]

    embedding_layer = Embedding(vocab_length + 1, output_dim, trainable=True)
    embedding_layer.build((None,))
    embedding_layer.set_weights([emb_matrix])

    return embedding_layer


def get_model(input_shape, embedding_layer, classes=6):
    sentence_indices = Input(shape=input_shape, dtype='int32')

    embeddings = embedding_layer(sentence_indices)
    # embeddings = Embedding(embedding_layer + 1, 200, input_length=input_shape[0])(sentence_indices)
    # recurrent_regularizer=l1_l2(0.01,0.01)
    # activity_regularizer=l1_l2(0.01, 0.01)
    # kernel_regularizer=l1_l2(0.01, 0.01)
    # bias_regularizer=l1_l2(0.01, 0.01)

    x = Bidirectional(LSTM(units=128, bias_regularizer=l1_l2(0.01, 0.01), return_sequences=False))(embeddings)
    x = Dropout(rate=0.5)(x)
    # x = Bidirectional(LSTM(units=256))(x)
    # x = Dropout(rate=0.5)(x)
    x = Dense(units=classes, activation="softmax")(x)

    return Model(inputs=sentence_indices, outputs=x)
