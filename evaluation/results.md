| Metric | Result |
|---|---:|
| Total tasks | 15 |
| Passed first attempt | 10 |
| pass@1 | 66.7% |
| Fixed after retry | 0 |
| Final passed | 10 |
| pass-after-retry | 66.7% |

| Task | Category | First attempt | Retry | Final | Time (s) |
|---|---|---|---|---|---:|
| T01 Prime number check | Basic Python | PASS | - | PASS | 24.1 |
| T02 Largest number in a list | Basic Python | PASS | - | PASS | 5.7 |
| T03 FizzBuzz list | Basic Python | PASS | - | PASS | 6.5 |
| T04 Palindrome check | Edge cases | PASS | - | PASS | 5.8 |
| T05 Nth Fibonacci number | Algorithms | PASS | - | PASS | 6.7 |
| T06 Binary search | Algorithms | PASS | - | PASS | 6.0 |
| T07 Two-sum indices | Algorithms | PASS | - | PASS | 6.3 |
| T08 Valid brackets | Data structures | PASS | - | PASS | 7.3 |
| T09 Merge sorted lists | Data structures | PASS | - | PASS | 16.3 |
| T10 Top-k frequent numbers | Data structures | PASS | - | PASS | 16.4 |
| T11 Standardize a tensor (PyTorch) | PyTorch | FAIL | FAIL | FAIL | 32.4 |
| T12 GAN generator (PyTorch) | GAN | FAIL | FAIL | FAIL | 31.6 |
| T13 GAN discriminator (PyTorch) | GAN | FAIL | FAIL | FAIL | 32.7 |
| T14 VAE reparameterization trick (PyTorch) | VAE | FAIL | FAIL | FAIL | 26.2 |
| T15 VAE KL-divergence loss (PyTorch) | VAE | FAIL | FAIL | FAIL | 23.2 |

| Hallucination check | Result |
|---|---:|
| Solutions generated | 45 |
| Flagged (invented import / blocked call / missing function) | 0 |
| Flag rate | 0.0% |

| Prompt technique | pass@1 |
|---|---:|
| Basic | 20.0% |
| Structured | 66.7% |

**Failure case:** T11 Standardize a tensor (PyTorch) - Failed visible test tuple(standardize(torch.tensor([[1.,2.],[3.,4.],[5.,6.]])).shape): rt asyncio
  File "C:\Users\MAHI KUSHWAHA\AppData\Local\Programs\Python\Python313\Lib\asyncio\__init__.py", line 43, in <module>
    from .windows_events import *
  File "C:\Users\MAHI KUSHWAHA\AppData\Local\Programs\Python\Python313\Lib\asyncio\windows_events.py", line 8, in <module>
    import _overlapped
OSError: [WinError 10106] The requested service provider could not be loaded or initialized