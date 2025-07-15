import asyncio
import logging
from typing import List, Dict, Tuple, Optional
from datasets import load_dataset
from sklearn.model_selection import train_test_split
import pandas as pd
from utils.config import settings

logger = logging.getLogger(__name__)

class MedicalDatasetLoader:
    def __init__(self):
        self.dataset_name = settings.DATASET_NAME
        self.train_split_ratio = settings.TRAIN_SPLIT_RATIO
        
    async def load_dataset(self) -> Dict:
        """Load medical dataset from Hugging Face"""
        logger.info(f"Loading dataset: {self.dataset_name}")
        
        try:
            if self.dataset_name == "medmcqa":
                dataset = load_dataset("openlifescienceai/medmcqa")
                return self._process_medmcqa(dataset)
            elif self.dataset_name == "pubmed_qa":
                dataset = load_dataset("pubmed_qa", "pqa_labeled")
                return self._process_pubmed_qa(dataset)
            else:
                raise ValueError(f"Unsupported dataset: {self.dataset_name}")
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            raise
    
    def _process_medmcqa(self, dataset) -> Dict:
        """Process MedMCQA dataset"""
        train_data = dataset['train']
        
        processed_data = []
        for item in train_data:
            processed_item = {
                'question': item['question'],
                'answer': item['exp'],  # explanation as answer
                'options': [item['opa'], item['opb'], item['opc'], item['opd']],
                'correct_option': item['cop'],
                'subject': item['subject_name'],
                'topic': item['topic_name'],
                'id': item['id']
            }
            processed_data.append(processed_item)
        
        return self._split_data(processed_data)
    
    def _process_pubmed_qa(self, dataset) -> Dict:
        """Process PubMed QA dataset"""
        train_data = dataset['train']
        
        processed_data = []
        for item in train_data:
            processed_item = {
                'question': item['question'],
                'answer': item['long_answer'],
                'context': ' '.join(item['context']['contexts']),
                'final_decision': item['final_decision'],
                'id': item['pubid']
            }
            processed_data.append(processed_item)
        
        return self._split_data(processed_data)
    
    def _split_data(self, data: List[Dict]) -> Dict:
        """Split data into train and evaluation sets"""
        train_data, eval_data = train_test_split(
            data,
            train_size=self.train_split_ratio,
            random_state=42,
            shuffle=True
        )
        
        logger.info(f"Dataset split: {len(train_data)} training, {len(eval_data)} evaluation")
        
        return {
            'train': train_data,
            'eval': eval_data,
            'total_size': len(data)
        }
    
    async def get_medical_categories(self) -> List[str]:
        """Get medical categories from dataset"""
        data = await self.load_dataset()
        
        if self.dataset_name == "medmcqa":
            categories = list(set([item['subject'] for item in data['train']]))
        else:  # pubmed_qa
            categories = ["General Medicine", "Clinical Medicine", "Biomedical Research"]
        
        return sorted(categories)