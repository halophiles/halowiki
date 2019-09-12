#!/usr/bin/env python3
# encoding: utf-8
import glob
import os
from operator import itemgetter
from metapub import PubMedFetcher
import sys

def main():
    '''
    Collects all .ris citation files from the publications folder
    and generates a Publications.md in the wiki folder
    containing all important information.
    '''

    #Collect .ris files
    ris_files = []
    for ris in glob.glob(
        os.path.join(
            'publications',
            '**',
            '*.ris'   
        ),
        recursive=True
    ):
        ris_files.append(ris)

    #Extract information from ris files
    #and store it in a dictionary
    publications_dict = {}
    all_ris_doi = set()
    for fullpath in ris_files:
        head, ris = os.path.split(fullpath)
        subfolder = os.path.basename(head)
        if subfolder not in publications_dict.keys():
            publications_dict[subfolder] = {}
        with open(fullpath, 'r') as in_file:
            tmp_dict = {
                'Authors': []
            }
            doi = None
            for line in in_file:
                l = line.strip()
                if l[:2] in ['A1', 'AU']:
                    tmp_dict['Authors'].append(
                        l.split('  - ')[1]
                    )
                elif l[:2] in ['T1', 'TI']:
                    title = l.split('  - ')[1].replace('&lt;em&gt;', '').replace('&lt;/em&gt;', '')
                    tmp_dict['Title'] = title
                elif l[:2] in ['Y1', 'DA','PY']:
                    year = int(l.split('  - ')[1].split('/')[0])
                    tmp_dict['Year'] = year
                elif l[:2] in ['JO', 'JF', 'T2']:
                    tmp_dict['Journal'] = l.split('  - ')[1]
                elif l[:2] in ['VL']:
                    tmp_dict['Volume'] = l.split('  - ')[1]
                elif l[:2] in ['IS']:
                    tmp_dict['Issue'] = l.split('  - ')[1]
                elif l[:2] in ['UR']:
                    tmp_dict['URL'] = l.split('  - ')[1]
                elif l[:2] in ['N2', 'AB']:
                    tmp_dict['Abstract'] = l.split('  - ')[1]
                elif l[:2] in ['DO', 'M3', 'N1']:
                    doi_line = l.split('  - ')[1].replace('doi:', '')
                    doi = '/'.join(doi_line.split('/')[-2:])
                    tmp_dict['DOI'] = doi
            for k in ['Title', 'Authors', 'Year', 'Journal', 'URL', 'DOI']:
                if k not in tmp_dict.keys():
                    print('''
                        {0} is required but could not be found
                        for {1}
                    '''.format(
                            k,
                            fullpath
                        )
                    )
                    sys.exit(1)
            for k in ['Volume', 'Issue', 'Abstract']:
                if k not in tmp_dict.keys():
                    tmp_dict[k] = ''
            publications_dict[subfolder][doi] = tmp_dict
            publications_dict[subfolder][doi]['Authors'] = '; '.join(tmp_dict['Authors'])
            citation_file = 'https://github.com/halophiles/halowiki//tree/master/publications/{0}/{1}'.format(
                subfolder,
                ris
            )
            publications_dict[subfolder][doi]['Citation'] = citation_file
            all_ris_doi.add(doi)

    #Fetching publications from PubMed
    #and store their info in the same dict
    pm_fetch = PubMedFetcher()
    hfx_pmids = pm_fetch.pmids_for_query('Haloferax volcanii')
    known_problems = [
        '29906440',
        '29888297',
        '29038254',
        '28660233',
        '25954264',
        '24240572',
    ]
    for pmid in hfx_pmids:
        if pmid in known_problems:
            continue
        try:
            article = pm_fetch.article_by_pmid(pmid)
            doi = '/'.join(article.doi.split('/')[-2:])
            tmp_dict = {}
            tmp_dict['Authors'] = '; '.join(article.authors)
            tmp_dict['Title'] = article.title.replace('&lt;em&gt;', '').replace('&lt;/em&gt;', '')
            tmp_dict['Year'] = int(article.year)
            tmp_dict['Journal'] = article.journal
            tmp_dict['Volume'] = article.volume
            tmp_dict['Issue'] = article.issue
            tmp_dict['URL'] = article.url
            tmp_dict['Abstract'] = article.abstract.replace('~', '')
            tmp_dict['DOI'] = doi
            tmp_dict['Citation'] = ''
        except:
            print('unsuccessful for {0}'.format(pmid))
            continue
        if doi in all_ris_doi:
            continue
        publications_dict['Others'][doi] = tmp_dict

    #Write markdown file for wiki
    #based on info in dict
    output_filename = os.path.join(
        'wiki',
        'Publications.md'
    )
    total_pubs = 0
    with open(output_filename, 'w', encoding="utf-8") as out_file:
        print('# Publications [ ](# )', file=out_file)
        print('', file=out_file)
        for subheading in sorted(publications_dict.keys()):
            print(' * [{0}](#{1})'.format(
                subheading.replace ('_', ' '),
                subheading.replace(' ', '-').lower()
            ), file=out_file)
        print('', file=out_file)
        for subheading in sorted(publications_dict.keys()):
            print('## {0}'.format(subheading.replace ('_', ' ')), file=out_file)
            print('', file=out_file)
            pub_list = []
            for pub in publications_dict[subheading].keys():
                try:
                    publications_dict[subheading][pub]['Lead Author'] = publications_dict[subheading][pub]['Authors'][0]
                    pub_list.append(publications_dict[subheading][pub])
                except:
                    print(pub)
                    print(publications_dict[subheading][pub]['Authors'])
            for pub in sorted(
                pub_list,
                key=itemgetter('Year', 'Lead Author'),
                reverse=True,
            ):
                total_pubs += 1
                print(
'''*{Title}*<br/>
{Authors}<br/>
**{Year}**<br/>
{Journal} {Volume}({Issue})<br/>
{DOI}
<details>
<summary>Abstract and Links</summary>

[Link to Publication]({URL})<br/>
[Citation]({Citation})<br/>
{Abstract}<br/>
</details><br/>

---
'''.format(**pub), file=out_file)

            print(
'''[Go to top of page](# )<br/>
----''',
                file=out_file
            )
    print('Total Number of Publications written to Publications.md:')
    print(total_pubs)

if __name__ == '__main__':
    main()