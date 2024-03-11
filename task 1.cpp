#include<iostream>
using namespace std;
int main()
{
	float num1,num2,c;
	int option;
	do
	{
		cout<<"1.addition\n";
		cout<<"2.subtraction\n";
		cout<<"3.multiplication\n";
		cout<<"4.division\n";
		cout<<"5.exit\n";
		cout<<"enter your option :";
		cin>>option;
		if(option>=1 && option<=4)
		{
			cout<<"enter num1 and num2:";
			cin>>num1>>num2;
			
		}
		switch(option)
		{
			case 1:
				c=num1+num2;
				cout<<"\n result="<<c;
				break;
			case 2:
				c=num1-num2;
				cout<<"\n result="<<c;
				break;
			case 3:
				c=num1*num2;
				cout<<"\n result="<<c;
				break;
			case 4:
				c=num1/num2;
				cout<<"\n result="<<c;
				break;
			case 5:
				return 0;
			default:
			   cout<<"wrong option";
			   break;
		}
		cout<<"\n_____________________________\n";
	}
	while(option!=5);
	cout<<endl;
	return 0;
}

			   
				
				
				
