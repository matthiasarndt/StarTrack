
class Info:
    print_info = True

    @classmethod
    def print_logo(cls):
        if cls.print_info:
            logo = r'''  
  \
   \
    \   ___  _                    
     \/ ___|| |_ __ _ _ __           
      \___ \| __/ _` | '__|             			
       ___) | || (_| | |               /
      |____/_\__\__,_|_|        _     /
     /     |_   _| __ __ _  ___| | __/
    /        | || '__/ _` |/ __| |/ /
   /         | || | | (_| | (__|   < 
  /          |_||_|  \__,_|\___|_|\_\
                                     \
                                      \
                                       \  

Version: 0.2.3
Author: Matthias Arndt 				                        
            '''
            print(logo)


if __name__ == '__main__':
    Info.print_logo()

