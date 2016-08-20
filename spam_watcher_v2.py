import praw
import re
import ast
import time
import datetime

# variables

subreddit_list = ['xxxxxxx', 'xxxxxxx', 'xxxxxxx', 'xxxxxxx']
whitelist_wiki = 'spam_watcher'

username = xxxxxxx
password = xxxxxxx

# functions

def current_time():
    return str(datetime.datetime.now())

def retrieve_whitelist(find_type, content, extract_list):
    whitelist = find_type.search(content)
    if whitelist is None:
        return []
    elif whitelist is not None:
        whitelist = whitelist.group()
        whitelist = extract_list.search(whitelist)
        whitelist = whitelist.group()
        whitelist = ast.literal_eval(whitelist)
        return whitelist


def retrieve_percentage(type, content):
    percentage = type.search(wiki_content)
    if percentage is None:
        return 0.20
    elif percentage is not None:
        percentage = percentage.group()
        percentage = percentage.split(' = ')
        percentage = float(float(percentage[1]) / float(100))
        return percentage


def retrieve_subreddit():
    for s in subreddit_list:
        yield s


def most_recent_submission(submissions):
    for x in submissions:
        if str(x.subreddit) == subreddit:
            return x


def report(submission_ratio, domain, recent_submission, subreddit, author):
    ratio = str(str(int(round((submission_ratio * 100), 0))) + '%')
    message = 'domain: ' + domain + ', ratio: ' + ratio
    recent_submission.report(reason=message)
    print(current_time() + ' ***REPORTED***, domain: ' + domain + ', percentage: ' + ratio)
    new_file.write(str(current_time()) + '\t/r/' + subreddit + '\t/u/' + author + '\t' + domain + '\t' + ratio + '\n')    


# initiate praw

r = praw.Reddit(user_agent='/u/multi-mod test script')
r.login(username, password, disable_warning=True)

Errors = praw.errors.HTTPException

#initiate logs

log = {}
for s in subreddit_list:
    log[s] = []

new_file = open('report_log.txt', 'a')
new_file.write('time\tsubreddit\tuser\tdomain\tpercentage\n')

#fight spam

while True:

    try:

        for subreddit in retrieve_subreddit():
            
            print(current_time() + ' subreddit: /r/' + subreddit)
            
            #retrieve whitelists
        
            find_domain_whitelist = re.compile('domain_whitelist = \[.*\]')
            find_user_whitelist = re.compile('user_whitelist = \[.*\]')
            extract_list = re.compile('\[.*\]')
            find_percentage = re.compile('percentage = \d{1,3}')
            
            wiki_page = r.get_wiki_page(subreddit, whitelist_wiki)
            wiki_content = str(wiki_page.content_md)
                
            domain_whitelist = retrieve_whitelist(find_domain_whitelist, wiki_content, extract_list)             
            user_whitelist = retrieve_whitelist(find_user_whitelist, wiki_content, extract_list)                
            percentage = retrieve_percentage(find_percentage, wiki_content)
            
            #spam check
            
            new_submissions = r.get_subreddit(subreddit).get_new(limit=25)
            authors = (x.author for x in new_submissions if x.id not in log[subreddit])
            
            for author in authors:
            
                if str(author) not in user_whitelist:
                
                    submissions = [x for x in author.get_submitted(limit=1000)]
                    recent_submission = most_recent_submission(submissions)
                    
                    if str(recent_submission.domain) not in domain_whitelist and recent_submission.is_self is False and str(recent_submission.id) not in log[subreddit]:
                        
                        print(current_time() + ' user: /u/' + str(author))
                    
                        domain = str(recent_submission.domain)
                        domains = [str(x.domain) for x in submissions if x.is_self is False]
                            
                        domain_count = float(domains.count(domain))
                        submission_count = float(len(submissions))
                        submission_ratio = float(domain_count / submission_count)
                        
                        author_name = str(author)                        
                        
                        if int(submission_count) < int(3):
                            pass
                        
                        elif int(submission_count) <= int(5) and submission_ratio >= float(0.75):
                            report(submission_ratio, domain, recent_submission, subreddit, author_name)
                        
                        elif int(submission_count) < int(10) and submission_ratio >= float(0.65):
                            report(submission_ratio, domain, recent_submission, subreddit, author_name)
                        
                        elif int(submission_count) >= int(10) and submission_ratio >= float(percentage):
                            report(submission_ratio, domain, recent_submission, subreddit, author_name)
                                      
                    if str(recent_submission.id) not in log[subreddit]:                      
                        log[subreddit].append(str(recent_submission.id))
                        
                    while True:
                        if len(log[subreddit]) > 100:
                            log_contents = log[subreddit]
                            del log_contents[0]
                            log[subreddit] = log_contents
                        elif len(log[subreddit]) <= 100:
                            break
        
        print(current_time() + ' --- sleeping for 30 seconds ---')                    
        time.sleep(30)
        
    except Errors:
        print(current_time() + ' Reddit may be down. Sleeping for 60 seconds')
        time.sleep(60)