import csv
import itertools
import sys

PROBS = {

 
    "gene": {
        2: 0.01,
        1: 0.03,
        0: 0.96
    },

    "trait": {

        # Probability of trait with two copies of gene
        2: {
            True: 0.65,
            False: 0.35
        },

        # Probability of trait with one copy of gene
        1: {
            True: 0.56,
            False: 0.44
        },

        # Probability of trait with no gene
        0: {
            True: 0.01,
            False: 0.99
        }
    },

    # Mutation probability
    "mutation": 0.01
}


def main():


    if len(sys.argv) != 2:
        sys.exit("Usage: python heredity.py data.csv")
    people = load_data(sys.argv[1])

    # Keep track of gene and trait probabilities for each person
    probabilities = {
        person: {
            "gene": {
                2: 0,
                1: 0,
                0: 0
            },
            "trait": {
                True: 0,
                False: 0
            }
        }
        for person in people
    }

    # Loop over all sets of people who might have the trait
    names = set(people)
    for have_trait in powerset(names):

        # Check if current set of people violates known information
        fails_evidence = any(
            (people[person]["trait"] is not None and
             people[person]["trait"] != (person in have_trait))
            for person in names
        )
        if fails_evidence:
            continue

        # Loop over all sets of people who might have the gene
        for one_gene in powerset(names):
            for two_genes in powerset(names - one_gene):

                # Update probabilities with new joint probability
                p = joint_probability(people, one_gene, two_genes, have_trait)
                update(probabilities, one_gene, two_genes, have_trait, p)

    # Ensure probabilities sum to 1

    normalize(probabilities)

    # Print results
    for person in people:
        print(f"{person}:")
        for field in probabilities[person]:
            print(f"  {field.capitalize()}:")
            for value in probabilities[person][field]:
                p = probabilities[person][field][value]
                print(f"    {value}: {p:.4f}")


def load_data(filename):

    data = dict()
    with open(filename) as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row["name"]
            data[name] = {
                "name": name,
                "mother": row["mother"] or None,
                "father": row["father"] or None,
                "trait": (True if row["trait"] == "1" else
                          False if row["trait"] == "0" else None)
            }
    return data


def powerset(s):
    """
    Return a list of all possible subsets of set s.
    """
    s = list(s)
    return [
        set(s) for s in itertools.chain.from_iterable(
            itertools.combinations(s, r) for r in range(len(s) + 1)
        )
    ]


def joint_probability(people, one_gene, two_genes, have_trait):


    probability=1
    no_gene=set(people) - (one_gene | two_genes)

    for person in people:
        if people[person]["mother"] ==None and people[person]["father"] ==None: 
            if person in no_gene:
                trait_prob=prob_get_trait(person,PROBS["gene"][0],PROBS["trait"][0],have_trait)

            elif person in one_gene:
                trait_prob=prob_get_trait(person,PROBS["gene"][1],PROBS["trait"][1],have_trait)

            elif person in two_genes:
                trait_prob=prob_get_trait(person,PROBS["gene"][2],PROBS["trait"][2],have_trait)   

            probability*=trait_prob

        else:
            child_gene_probability=1
            mother_probability=prob_get_gene_from_parent(people[person]["mother"],one_gene,two_genes)
            father_probability=prob_get_gene_from_parent(people[person]["father"],one_gene,two_genes)

            if person in no_gene:
                child_gene_probability*=(1-mother_probability)*(1-father_probability)
                trait_prob=prob_get_trait(person,child_gene_probability,PROBS["trait"][0],have_trait)

            elif person in one_gene:
                child_gene_probability=(mother_probability*(1-father_probability)+(1-mother_probability)*father_probability)
                trait_prob=prob_get_trait(person,child_gene_probability,PROBS["trait"][1],have_trait)

            elif person in two_genes:
                child_gene_probability=mother_probability*father_probability
                trait_prob=prob_get_trait(person,child_gene_probability,PROBS["trait"][2],have_trait)

 
            probability*=trait_prob

    return probability
    raise NotImplementedError
def prob_get_trait(person,gene_probability,trait_probability,have_trait):
    '''
    After receiving the person and his gene probability ,it returns the full probability of him having or not having the trait
    '''
    if person in have_trait:
        prob=gene_probability*trait_probability[True]
    else:
        prob=gene_probability*trait_probability[False]
    return prob



def prob_get_gene_from_parent(parent,one_gene,two_genes):
    '''
    Returns the probability of a parent to transmit the gene to his child
    '''
    if parent in two_genes:
        return 1-PROBS["mutation"]
    elif parent in one_gene:
        return 0.5
    else:
        return PROBS["mutation"]


def update(probabilities, one_gene, two_genes, have_trait, p):

    for person in probabilities:
        if person in one_gene:
            probabilities[person]["gene"][1]+=p
        elif person in two_genes:
            probabilities[person]["gene"][2]+=p
        else:
            probabilities[person]["gene"][0]+=p
        if person in have_trait:
            probabilities[person]["trait"][True]+=p
        else:
            probabilities[person]["trait"][False]+=p



def normalize(probabilities):
    for person,aspects in probabilities.items():
        for aspect,values in aspects.items():
            max_value=sum(values.values())
            for key,value in values.items():
                values[key]=value/max_value*1




if __name__ == "__main__":
    main()
