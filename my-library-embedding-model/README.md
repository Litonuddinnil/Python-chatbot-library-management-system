---
tags:
- sentence-transformers
- sentence-similarity
- feature-extraction
- generated_from_trainer
- dataset_size:795
- loss:MultipleNegativesRankingLoss
base_model: sentence-transformers/all-MiniLM-L6-v2
widget:
- source_sentence: Search for the book computer networks
  sentences:
  - 'Book Title: structured programming language c programming. Author: . Department:
    cse. Semester: 1st. Description: the c programming language by kernighan and ritchie
    is the definitive reference for c programming. covers structured programming fundamentals,
    pointers, arrays, functions, and file io used in cse foundation courses..'
  - 'Book Title: computer networks. Author: . Department: cse. Semester: 5th. Description:
    covers osi model, tcpip, data link layer, network layer, transport layer, application
    layer protocols, network security, and wireless networks. comprehensive reference
    for computer networking courses..'
  - 'Book Title: cryptography and network security principles and practice. Author:
    . Department: cse. Semester: 7th. Description: covers symmetric and asymmetric
    encryption, des, aes, rsa, hash functions, digital signatures, ssltls, firewalls,
    and intrusion detection systems. comprehensive reference for network security
    courses..'
- source_sentence: I need the textbook for digital logic and computer design
  sentences:
  - 'Book Title: pattern recognition and machine learning. Author: . Department: cse.
    Semester: 7th. Description: covers bayesian decision theory, linear models, neural
    networks, kernel methods, graphical models, mixture models, em algorithm, and
    approximate inference. advanced reference for pattern recognition..'
  - 'Book Title: machine learning. Author: . Department: cse. Semester: 7th. Description:
    covers decision trees, neural networks, bayesian learning, instancebased learning,
    genetic algorithms, reinforcement learning, and analytical learning. foundational
    machine learning reference for cse students..'
  - 'Book Title: digital logic and computer design. Author: . Department: cse. Semester:
    2nd. Description: covers boolean algebra, logic gates, combinational circuits,
    sequential circuits, registers, counters, and memory units. essential reference
    for digital logic design course in cse programs..'
- source_sentence: I want to know about digital logic and computer design
  sentences:
  - 'Book Title: digital logic and computer design. Author: . Department: cse. Semester:
    2nd. Description: covers boolean algebra, logic gates, combinational circuits,
    sequential circuits, registers, counters, and memory units. essential reference
    for digital logic design course in cse programs..'
  - 'Book Title: structured programming language c programming. Author: . Department:
    cse. Semester: 1st. Description: the c programming language by kernighan and ritchie
    is the definitive reference for c programming. covers structured programming fundamentals,
    pointers, arrays, functions, and file io used in cse foundation courses..'
  - 'Book Title: engineering mathematics ii. Author: . Department: cse. Semester:
    2nd. Description: covers ordinary differential equations, laplace transforms,
    fourier series, partial differential equations, and complex variable analysis.
    continuation of engineering mathematics i for second semester cse students..'
- source_sentence: probability and statistics for engineering and the sciences boi
    ta ki library e ache?
  sentences:
  - 'Book Title: probability and statistics for engineering and the sciences. Author:
    . Department: cse. Semester: 4th. Description: covers probability theory, random
    variables, distributions, statistical inference, hypothesis testing, regression
    analysis, and quality control. standard probability and statistics text for engineering
    students..'
  - 'Book Title: bangladesh studies. Author: . Department: cse. Semester: 2nd. Description:
    covers the history of bangladesh, language movement, liberation war of 1971, constitutional
    development, socioeconomic conditions, and professional ethics for undergraduate
    engineering students..'
  - 'Book Title: microprocessors and interfacing programming and hardware. Author:
    . Department: cse. Semester: 5th. Description: covers 80868088 microprocessor
    architecture, assembly language programming, interrupt handling, memory interfacing,
    and peripheral devices. standard reference for microprocessor courses in bangladeshi
    universities..'
- source_sentence: I want to know about communicative english for undergraduate students
  sentences:
  - 'Book Title: machine learning. Author: . Department: cse. Semester: 7th. Description:
    covers decision trees, neural networks, bayesian learning, instancebased learning,
    genetic algorithms, reinforcement learning, and analytical learning. foundational
    machine learning reference for cse students..'
  - 'Book Title: pattern recognition and machine learning. Author: . Department: cse.
    Semester: 7th. Description: covers bayesian decision theory, linear models, neural
    networks, kernel methods, graphical models, mixture models, em algorithm, and
    approximate inference. advanced reference for pattern recognition..'
  - 'Book Title: communicative english for undergraduate students. Author: . Department:
    cse. Semester: 1st. Description: communicative english textbook designed for undergraduate
    engineering students in bangladesh. covers reading, writing, listening, and speaking
    skills for academic and professional communication..'
pipeline_tag: sentence-similarity
library_name: sentence-transformers
---

# SentenceTransformer based on sentence-transformers/all-MiniLM-L6-v2

This is a [sentence-transformers](https://www.SBERT.net) model finetuned from [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2). It maps sentences & paragraphs to a 384-dimensional dense vector space and can be used for retrieval.

## Model Details

### Model Description
- **Model Type:** Sentence Transformer
- **Base model:** [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) <!-- at revision 1110a243fdf4706b3f48f1d95db1a4f5529b4d41 -->
- **Maximum Sequence Length:** 256 tokens
- **Output Dimensionality:** 384 dimensions
- **Similarity Function:** Cosine Similarity
- **Supported Modality:** Text
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/huggingface/sentence-transformers)
- **Hugging Face:** [Sentence Transformers on Hugging Face](https://huggingface.co/models?library=sentence-transformers)

### Full Model Architecture

```
SentenceTransformer(
  (0): Transformer({'transformer_task': 'feature-extraction', 'modality_config': {'text': {'method': 'forward', 'method_output_name': 'last_hidden_state'}}, 'module_output_name': 'token_embeddings', 'architecture': 'BertModel'})
  (1): Pooling({'embedding_dimension': 384, 'pooling_mode': 'mean', 'include_prompt': True})
  (2): Normalize({})
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```
Then you can load this model and run inference.
```python
from sentence_transformers import SentenceTransformer

# Download from the 🤗 Hub
model = SentenceTransformer("sentence_transformers_model_id")
# Run inference
sentences = [
    'I want to know about communicative english for undergraduate students',
    'Book Title: communicative english for undergraduate students. Author: . Department: cse. Semester: 1st. Description: communicative english textbook designed for undergraduate engineering students in bangladesh. covers reading, writing, listening, and speaking skills for academic and professional communication..',
    'Book Title: machine learning. Author: . Department: cse. Semester: 7th. Description: covers decision trees, neural networks, bayesian learning, instancebased learning, genetic algorithms, reinforcement learning, and analytical learning. foundational machine learning reference for cse students..',
]
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 384]

# Get the similarity scores for the embeddings
similarities = model.similarity(embeddings, embeddings)
print(similarities)
# tensor([[1.0000, 0.8952, 0.0274],
#         [0.8952, 1.0000, 0.1012],
#         [0.0274, 0.1012, 1.0000]])
```
<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 795 training samples
* Columns: <code>sentence_0</code> and <code>sentence_1</code>
* Approximate statistics based on the first 100 samples:
  |          | sentence_0                                                                        | sentence_1                                                                         |
  |:---------|:----------------------------------------------------------------------------------|:-----------------------------------------------------------------------------------|
  | type     | string                                                                            | string                                                                             |
  | modality | text                                                                              | text                                                                               |
  | details  | <ul><li>min: 6 tokens</li><li>mean: 12.04 tokens</li><li>max: 24 tokens</li></ul> | <ul><li>min: 22 tokens</li><li>mean: 61.39 tokens</li><li>max: 73 tokens</li></ul> |
* Samples:
  | sentence_0                                                                | sentence_1                                                                                                                                                                                                                                                                                                                                   |
  |:--------------------------------------------------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
  | <code>Query regarding distributed systems principles and paradigms</code> | <code>Book Title: distributed systems principles and paradigms. Author: . Department: cse. Semester: 7th. Description: covers distributed system architectures, communication, naming, synchronization, consistency and replication, fault tolerance, and distributed file systems. comprehensive reference for distributed systems..</code> |
  | <code>Find software engineering in books list</code>                      | <code>Book Title: software engineering. Author: . Department: cse. Semester: 5th. Description: covers software development life cycle, requirements engineering, design patterns, uml, testing strategies, project management, and agile methodologies. the standard reference for software engineering courses..</code>                     |
  | <code>Query regarding engineering mathematics i</code>                    | <code>Book Title: engineering mathematics i. Author: . Department: cse. Semester: 1st. Description: covers differential calculus, integral calculus, vector calculus, matrix algebra, and coordinate geometry for engineering applications. standard reference for first year cse mathematics..</code>                                       |
* Loss: [<code>MultipleNegativesRankingLoss</code>](https://sbert.net/docs/package_reference/sentence_transformer/losses.html#multiplenegativesrankingloss) with these parameters:
  ```json
  {
      "scale": 20.0,
      "similarity_fct": "cos_sim",
      "gather_across_devices": false,
      "directions": [
          "query_to_doc"
      ],
      "partition_mode": "joint",
      "hardness_mode": null,
      "hardness_strength": 0.0
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `per_device_train_batch_size`: 16
- `num_train_epochs`: 5
- `per_device_eval_batch_size`: 16
- `multi_dataset_batch_sampler`: round_robin

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `per_device_train_batch_size`: 16
- `num_train_epochs`: 5
- `max_steps`: -1
- `learning_rate`: 5e-05
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: None
- `warmup_steps`: 0
- `optim`: adamw_torch_fused
- `optim_args`: None
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `optim_target_modules`: None
- `gradient_accumulation_steps`: 1
- `average_tokens_across_devices`: True
- `max_grad_norm`: 1
- `label_smoothing_factor`: 0.0
- `bf16`: False
- `fp16`: False
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `use_cache`: False
- `neftune_noise_alpha`: None
- `torch_empty_cache_steps`: None
- `auto_find_batch_size`: False
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `include_num_input_tokens_seen`: no
- `log_level`: passive
- `log_level_replica`: warning
- `disable_tqdm`: False
- `project`: huggingface
- `trackio_space_id`: None
- `trackio_bucket_id`: None
- `trackio_static_space_id`: None
- `per_device_eval_batch_size`: 16
- `prediction_loss_only`: True
- `eval_on_start`: False
- `eval_do_concat_batches`: True
- `eval_use_gather_object`: False
- `eval_accumulation_steps`: None
- `include_for_metrics`: []
- `batch_eval_metrics`: False
- `save_only_model`: False
- `save_on_each_node`: False
- `enable_jit_checkpoint`: False
- `push_to_hub`: False
- `hub_private_repo`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_always_push`: False
- `hub_revision`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `restore_callback_states_from_checkpoint`: False
- `full_determinism`: False
- `seed`: 42
- `data_seed`: None
- `use_cpu`: False
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `parallelism_config`: None
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `dataloader_prefetch_factor`: None
- `remove_unused_columns`: True
- `label_names`: None
- `train_sampling_strategy`: random
- `length_column_name`: length
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `ddp_static_graph`: None
- `ddp_backend`: None
- `ddp_timeout`: 1800
- `fsdp`: None
- `fsdp_config`: None
- `deepspeed`: None
- `debug`: []
- `skip_memory_metrics`: True
- `do_predict`: False
- `resume_from_checkpoint`: None
- `warmup_ratio`: None
- `local_rank`: -1
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: round_robin
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Time
- **Training**: 4.8 minutes

### Framework Versions
- Python: 3.13.5
- Sentence Transformers: 5.6.0
- Transformers: 5.13.0
- PyTorch: 2.12.1+cpu
- Accelerate: 1.14.0
- Datasets: 5.0.0
- Tokenizers: 0.22.2

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

#### MultipleNegativesRankingLoss
```bibtex
@misc{oord2019representationlearningcontrastivepredictive,
      title={Representation Learning with Contrastive Predictive Coding},
      author={Aaron van den Oord and Yazhe Li and Oriol Vinyals},
      year={2019},
      eprint={1807.03748},
      archivePrefix={arXiv},
      primaryClass={cs.LG},
      url={https://arxiv.org/abs/1807.03748},
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->