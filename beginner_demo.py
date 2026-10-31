"""Small dependency-free example. Indices printed to the user are one-based."""
scores=[1,2,8,9,7,1]
k=3
current=sum(scores[i] for i in range(k))
best=current
start=0
print('Scores:',scores,'Window size:',k)
print('Window 1:',scores[:k],'sum =',current)
for right in range(k,len(scores)):
    outgoing=scores[right-k]
    incoming=scores[right]
    current=current-outgoing+incoming
    left=right-k+1
    print(f'Window {left+1}: subtract {outgoing}, add {incoming}, sum = {current}')
    if current>best:
        best=current
        start=left
print('Best start (one-based):',start+1)
print('Best window:',scores[start:start+k])
print('Best sum:',best)
