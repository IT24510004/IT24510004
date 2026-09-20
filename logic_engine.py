# logic_engine.py

# Lab 05 - Step 1.1 - Building the Knowledge Base (KB)
class KnowledgeBase:
    """A declarative Knowledge Base that stores facts and Horn clause rules, 
    and performs data-driven forward chaining inference using Modus Ponens."""

    def __init__(self):
        # Attributes
        self.facts = set()        # Stores unique string facts (e.g., "TargetVisible")
        self.rules = []           # Stores rules as Tuples: ( [list_of_premises], "conclusion_string" )

    def tell_fact(self, fact_string):
        """Add a new fact to the knowledge base facts set."""
        self.facts.add(fact_string)

    def tell_rule(self, premise_list, conclusion_string):
        """Add a new rule (Horn Clause) to the rules list."""
        self.rules.append((premise_list, conclusion_string))
        
    def clear_facts(self):
        """Empty the facts set for a new evaluation pass."""
        self.facts.clear()

    # Lab 05 - Step 2.1 - Implementation of Forward Chaining
    def forward_chain(self):
        """
        Data-driven forward chaining inference engine.
        Repeatedly evaluates rules using Modus Ponens until no new facts can be deduced.
        """
        new_facts_added = True
        
        while new_facts_added == True:
            new_facts_added = False
            
            for premises, conclusion in self.rules:
                if conclusion not in self.facts:
                    
                    # Modus Ponens Check: Check if all premises are present in facts
                    if all(p in self.facts for p in premises):
                        self.facts.add(conclusion)
                        new_facts_added = True