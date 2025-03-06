from abc import ABC, abstractmethod

class LLMInterface(ABC):
    @abstractmethod
    def generate(self, prompt):
        pass
    
    @abstractmethod
    def generate_chat_messages(self, messages):
        pass
